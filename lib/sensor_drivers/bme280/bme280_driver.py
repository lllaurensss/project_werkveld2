import time
import uuid
from enum import Enum

from lib.domain.sensor_data import SensorData
from lib.sensor_drivers.sensor_interface import SensorInterface


DEFAULT_PORT = 0x76


class SampleModes(Enum):
    SAMPLE_X1 = 1
    SAMPLE_X2 = 2
    SAMPLE_X4 = 3
    SAMPLE_X8 = 4
    SAMPLE_X16 = 5


class Reader(object):
    """
    Wraps a I2C SMBus instance to provide methods for reading
    signed/unsigned bytes and 16-bit words
    """

    def __init__(self, bus, address):
        self._bus = bus
        self._address = address

    def unsigned_short(self, register):
        return self._bus.read_word_data(self._address, register) & 0xffff

    def signed_short(self, register):
        word = self.unsigned_short(register)
        return word if word < 0x8000 else word - 0x10000

    def unsigned_byte(self, register):
        return self._bus.read_byte_data(self._address, register) & 0xff

    def signed_byte(self, register):
        byte = self.unsigned_byte(register) & 0xff
        return byte if byte < 0x80 else byte - 0x100


class UncompensatedReadings(object):

    def __init__(self, block):
        self._block = block
        self.pressure = (block[0] << 16 | block[1] << 8 | block[2]) >> 4
        self.temperature = (block[3] << 16 | block[4] << 8 | block[5]) >> 4
        self.humidity = block[6] << 8 | block[7]

    def __repr__(self):
        return "uncompensated_reading(temp=0x{0:08X}, pressure=0x{1:08X}, humidity=0x{2:08X}, block={3})".format(
            self.temperature, self.pressure, self.humidity,
            ":".join("{0:02X}".format(c) for c in self._block))


class CompensatedReadings(object):
    """
    Compensation formulas translated from Appendix A (8.1) of BME280 datasheet:

      * Temperature in °C, double precision. Output value of "51.23"
        equals 51.23 °C

      * Pressure in hPa as double. Output value of "963.862" equals
        963.862 hPa

      * Humidity in %rH as double. Output value of "46.332" represents
        46.332 %rH
    """

    def __init__(self, raw_readings, compensation_params):
        self._comp = compensation_params
        self.uncompensated = raw_readings
        self.temperature = self.__tfine(raw_readings.temperature) / 5120.0
        self.humidity = self.__calc_humidity(raw_readings.humidity,
                                             raw_readings.temperature)
        self.pressure = self.__calc_pressure(raw_readings.pressure,
                                             raw_readings.temperature) / 100.0

    def __tfine(self, t):
        v1 = (t / 16384.0 - self._comp.dig_T1 / 1024.0) * self._comp.dig_T2
        v2 = ((t / 131072.0 - self._comp.dig_T1 / 8192.0) ** 2) * self._comp.dig_T3
        return v1 + v2

    def __calc_humidity(self, h, t):
        res = self.__tfine(t) - 76800.0
        res = (h - (self._comp.dig_H4 * 64.0 + self._comp.dig_H5 / 16384.0 * res)) * (self._comp.dig_H2 / 65536.0 * (1.0 + self._comp.dig_H6 / 67108864.0 * res * (1.0 + self._comp.dig_H3 / 67108864.0 * res)))
        res = res * (1.0 - (self._comp.dig_H1 * res / 524288.0))
        return max(0.0, min(res, 100.0))

    def __calc_pressure(self, p, t):
        v1 = self.__tfine(t) / 2.0 - 64000.0
        v2 = v1 * v1 * self._comp.dig_P6 / 32768.0
        v2 = v2 + v1 * self._comp.dig_P5 * 2.0
        v2 = v2 / 4.0 + self._comp.dig_P4 * 65536.0
        v1 = (self._comp.dig_P3 * v1 * v1 / 524288.0 + self._comp.dig_P2 * v1) / 524288.0
        v1 = (1.0 + v1 / 32768.0) * self._comp.dig_P1

        # Prevent divide by zero
        if v1 == 0:
            return 0

        res = 1048576.0 - p
        res = ((res - v2 / 4096.0) * 6250.0) / v1
        v1 = self._comp.dig_P9 * res * res / 2147483648.0
        v2 = res * self._comp.dig_P8 / 32768.0
        res = res + (v1 + v2 + self._comp.dig_P7) / 16.0
        return res

    def __repr__(self):
        return ("compensated_reading(temp={0:0.3f} °C, pressure={1:0.2f} hPa, humidity={2:0.2f} % rH)"
                .format(self.temperature, self.pressure, self.humidity))


class Params(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.f(*args)
        return self.memo[args]


class Bme280(SensorInterface):
    def __init__(self, bus, address=DEFAULT_PORT, sampling=SampleModes.SAMPLE_X1) -> None:
        self._bus = bus
        self._address = address

        self._compensation_params = self.load_calibration_params()
        self._sampling = sampling

    def load_calibration_params(self):
        """
        The BME280 output consists of the ADC output values. However, each sensing
        element behaves differently. Therefore, the actual pressure and temperature
        must be calculated using a set of calibration parameters.

        The calibration parameters are subsequently used to with some compensation
        formula to perform temperature readout in degC, humidity in % and pressure
        in hPA.
        """
        read = Reader(self._bus, self._address)
        compensation_params = Params()

        # Temperature trimming params
        compensation_params.dig_T1 = read.unsigned_short(0x88)
        compensation_params.dig_T2 = read.signed_short(0x8A)
        compensation_params.dig_T3 = read.signed_short(0x8C)

        # Pressure trimming params
        compensation_params.dig_P1 = read.unsigned_short(0x8E)
        compensation_params.dig_P2 = read.signed_short(0x90)
        compensation_params.dig_P3 = read.signed_short(0x92)
        compensation_params.dig_P4 = read.signed_short(0x94)
        compensation_params.dig_P5 = read.signed_short(0x96)
        compensation_params.dig_P6 = read.signed_short(0x98)
        compensation_params.dig_P7 = read.signed_short(0x9A)
        compensation_params.dig_P8 = read.signed_short(0x9C)
        compensation_params.dig_P9 = read.signed_short(0x9E)

        # Humidity trimming params
        compensation_params.dig_H1 = read.unsigned_byte(0xA1)
        compensation_params.dig_H2 = read.signed_short(0xE1)
        compensation_params.dig_H3 = read.signed_byte(0xE3)

        e4 = read.signed_byte(0xE4)
        e5 = read.signed_byte(0xE5)
        e6 = read.signed_byte(0xE6)

        compensation_params.dig_H4 = e4 << 4 | e5 & 0x0F
        compensation_params.dig_H5 = ((e5 >> 4) & 0x0F) | (e6 << 4)
        compensation_params.dig_H6 = read.signed_byte(0xE7)

        return compensation_params

    def __calc_delay(self, t_oversampling, h_oversampling, p_oversampling) -> float:
        t_delay = 0.000575 + 0.0023 * (1 << t_oversampling)
        h_delay = 0.000575 + 0.0023 * (1 << h_oversampling)
        p_delay = 0.001250 + 0.0023 * (1 << p_oversampling)
        return t_delay + h_delay + p_delay

    def _sample(self) -> CompensatedReadings:
        """
        Primes the sensor for reading (default: x1 oversampling), pauses for a set
        amount of time so that the reading stabilizes, and then returns a
        compensated reading object with the following attributes:

          * timestamp (Python's ``datetime`` object) when reading was taken
          * temperature (in degrees Celsius)
          * humidity (in % relative humidity)
          * pressure (in hPa)
        """

        mode = 1  # forced
        t_oversampling = self._sampling.value or SampleModes.SAMPLE_X1.value
        h_oversampling = self._sampling.value or SampleModes.SAMPLE_X1.value
        p_oversampling = self._sampling.value or SampleModes.SAMPLE_X1.value

        self._bus.write_byte_data(self._address, 0xF2, h_oversampling)  # ctrl_hum
        self._bus.write_byte_data(self._address, 0xF4, t_oversampling << 5 | p_oversampling << 2 | mode)  # ctrl
        delay = self.__calc_delay(t_oversampling, h_oversampling, p_oversampling)
        time.sleep(delay)

        block = self._bus.read_i2c_block_data(self._address, 0xF7, 8)
        raw_data = UncompensatedReadings(block)
        return CompensatedReadings(raw_data, self._compensation_params)

    def get_sensor_data(self) -> SensorData:
        data = self._sample()
        return SensorData(temperature=data.temperature, pressure=data.pressure, humidity=data.humidity)

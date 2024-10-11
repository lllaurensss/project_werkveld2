from unittest import TestCase
from unittest.mock import MagicMock, patch

from lib.sensor_drivers.bme280.bme280_driver import BME280


class TestBME280(TestCase):
    @patch("lib.sensor_drivers.sensor_drivers.BME280")
    def setUp(self, MockDevice):
        self.mock_device = MockDevice.return_value
        self.bme280 = BME280(i2c_addr=0x76)

        self.mock_device.get.side_effect = lambda x: {
            "CHIP_ID": MagicMock(id=0x60),
            "CALIBRATION": MagicMock(dig_t1=27504, dig_t2=26435, dig_t3=-1000),
            "CALIBRATION2": MagicMock(dig_h1=75, dig_h2=362, dig_h3=0, dig_h4=324, dig_h5=50, dig_h6=30),
            "DATA": MagicMock(temperature=519888, pressure=415148, humidity=36808)
        }[x]

        self.bme280.calibration.compensate_temperature = MagicMock(return_value=25.6)
        self.bme280.calibration.compensate_pressure = MagicMock(return_value=1013.25)
        self.bme280.calibration.compensate_humidity = MagicMock(return_value=40.5)

    def test_get_temperature(self):
        temperature = self.bme280.get_temperature()
        self.assertEqual(temperature, 25.6)
        self.bme280.calibration.compensate_temperature.assert_called_once()

    def test_get_pressure(self):
        pressure = self.bme280.get_pressure()
        self.assertEqual(pressure, 1013.25)
        self.bme280.calibration.compensate_pressure.assert_called_once()

    def test_get_humidity(self):
        humidity = self.bme280.get_humidity()
        self.assertEqual(humidity, 40.5)
        self.bme280.calibration.compensate_humidity.assert_called_once()
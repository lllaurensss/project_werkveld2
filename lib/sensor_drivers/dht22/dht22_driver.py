import random

from lib.domain.sensor_data import SensorData
from lib.sensor_drivers.sensor_interface import SensorInterface


try:
    import Adafruit_DHT
    LIBRARY_AVAILABLE = True
except ImportError:
    print("Adafruit_DHT library not found, mocking sensor data.")
    LIBRARY_AVAILABLE = False


class Dht22(SensorInterface):

    def __init__(self, gpio_pin: int):
        self._sensor = Adafruit_DHT.DHT22 if LIBRARY_AVAILABLE else None
        self._gpio_pin = gpio_pin

    def _read_data(self) -> SensorData:
        if LIBRARY_AVAILABLE:
            humidity, temperature = Adafruit_DHT.read(self._sensor, self._gpio_pin)
        else:
            humidity = round(random.uniform(20.0, 90.0), 2)
            temperature = round(random.uniform(15.0, 35.0), 2)

        return SensorData(
            temperature=temperature,
            pressure=0,
            humidity=humidity
        )

    def get_sensor_data(self) -> SensorData:
        try:
            sensor_data = self._read_data()
            return sensor_data
        except Exception as e:
            print(f"Failed to get sensor data: {e}")
            return SensorData()  # Return an empty object in case of an error

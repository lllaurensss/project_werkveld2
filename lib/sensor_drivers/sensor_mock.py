import random

from lib.sensor_drivers.sensor_interface import SensorInterface


class Bme280Mock(SensorInterface):

    def setup(self, mode="normal", temperature_oversampling=16, pressure_oversampling=16, humidity_oversampling=16, temperature_standby=500) -> None:
        pass

    def get_temperature(self) -> float:
        # Random temperature between -10.0 and 40.0 °C
        return round(random.uniform(-10.0, 40.0), 2)

    def get_pressure(self, full_file_name: str) -> float:
        # Random atmospheric pressure between 950 and 1050 hPa
        return round(random.uniform(950, 1050), 2)

    def get_humidity(self) -> float:
        # Random humidity between 0% and 100%
        return round(random.uniform(0, 100), 2)

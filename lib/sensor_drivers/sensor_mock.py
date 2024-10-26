import random
import uuid

from lib.domain.sensor_data import SensorData
from lib.sensor_drivers.sensor_interface import SensorInterface


class SensorMock(SensorInterface):

    def _get_temperature(self) -> float:
        # Random temperature between -10.0 and 40.0 °C
        return round(random.uniform(-10.0, 40.0), 2)

    def _get_pressure(self) -> float:
        # Random atmospheric pressure between 950 and 1050 hPa
        return round(random.uniform(950, 1050), 2)

    def _get_humidity(self) -> float:
        # Random humidity between 0% and 100%
        return round(random.uniform(0, 100), 2)

    def get_sensor_data(self) -> SensorData:
        return SensorData(temperature=self._get_temperature(),
                          humidity=self._get_humidity(),
                          pressure=self._get_pressure())

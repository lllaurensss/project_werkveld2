from lib.domain.sensor_data import SensorData


class SensorInterface:

    def get_sensor_data(self) -> SensorData:
        return SensorData()

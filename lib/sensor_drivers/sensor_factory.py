from lib.sensor_drivers.sensor_driver import SensorDriver
from lib.sensor_drivers.sensor_interface import SensorInterface


class SensorFactory:

    @staticmethod
    def create_driver(sensor_driver: SensorDriver) -> SensorInterface:
        if sensor_driver == SensorDriver.MOCK:
            from lib.sensor_drivers.sensor_mock import Bme280Mock
            return Bme280Mock()
        if sensor_driver == SensorDriver.BME280:
            from lib.sensor_drivers.bme280.bme280_driver import BME280
            return BME280()

        raise ValueError(f"Unsupported sensor driver: {sensor_driver}")

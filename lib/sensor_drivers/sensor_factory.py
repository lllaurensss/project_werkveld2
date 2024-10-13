from lib.sensor_drivers.sensor_driver import SensorDriver
from lib.sensor_drivers.sensor_interface import SensorInterface


class SensorFactory:

    @staticmethod
    def create_driver(sensor_driver: SensorDriver) -> SensorInterface:
        if sensor_driver == SensorDriver.MOCK:
            from lib.sensor_drivers.sensor_mock import SensorMock

            return SensorMock()
        if sensor_driver == SensorDriver.BME280:
            from lib.sensor_drivers.bme280.bme280_driver import Bme280
            import smbus2

            port = 1
            bus = smbus2.SMBus(port)
            return Bme280(bus)

        raise ValueError(f"Unsupported sensor driver: {sensor_driver}")

from logging import Logger

from lib.domain.sensor_data import SensorData
from lib.mqtt.mqtt_topic import MqttTopic
from lib.sensor_drivers.sensor_driver import SensorDriver
from lib.sensor_drivers.sensor_factory import SensorFactory
from lib.mqtt.mqtt_manager import MQTTManager


class EnviroSenseSensorApplication:

    def __init__(self, digital_id: str, logger: Logger, sensor_driver_as_str: str, mqtt_manager: MQTTManager):
        self._digital_id = digital_id
        self._logger = logger

        self._sensor_driver = self._set_sensor_driver(sensor_driver_as_str)
        self._sensor = SensorFactory.create_driver(self._sensor_driver)

        self._mqtt_manager = mqtt_manager
        self._mqtt_topic = MqttTopic(self._digital_id)

    def _set_sensor_driver(self, sensor_driver_as_str: str) -> SensorDriver:
        if sensor_driver_as_str.lower() == "mock":
            return SensorDriver.MOCK
        elif sensor_driver_as_str.lower() == "bme280":
            return SensorDriver.BME280
        else:
            raise ValueError(f"Unsupported sensor driver: {sensor_driver_as_str}")

    def publish_sensor_data(self):
        sensor_data = self._sensor.get_sensor_data()
        payload = sensor_data.to_json()
        topic = self._mqtt_topic.sensor_data_topic

        self._mqtt_manager.publish(topic, payload)

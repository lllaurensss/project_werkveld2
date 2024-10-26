import uuid
from logging import Logger

from lib.domain.sensor_data import SensorData
from lib.domain.sensor_data_payload import SensorDataPayload
from lib.mqtt.mqtt_topic import MqttTopic
from lib.sensor_drivers.sensor_driver import SensorDriver
from lib.sensor_drivers.sensor_factory import SensorFactory
from lib.mqtt.mqtt_manager import MQTTManager


class EnviroSenseSensorApplication:

    def __init__(self, digital_id: str, logger: Logger, internal_sensor_driver_as_str: str, external_sensor_driver_as_str: str, mqtt_manager: MQTTManager):
        self._digital_id = digital_id
        self._logger = logger

        self._internal_sensor_driver = self._set_sensor_driver(internal_sensor_driver_as_str)
        self._external_sensor_driver = self._set_sensor_driver(external_sensor_driver_as_str)

        self._internal_sensor = SensorFactory.create_driver(self._internal_sensor_driver)
        self._external_sensor = SensorFactory.create_driver(self._external_sensor_driver)

        self._mqtt_manager = mqtt_manager
        self._mqtt_topic = MqttTopic(self._digital_id)

    def _set_sensor_driver(self, sensor_driver_as_str: str) -> SensorDriver:
        if sensor_driver_as_str.lower() == "mock":
            return SensorDriver.MOCK
        elif sensor_driver_as_str.lower() == "bme280":
            return SensorDriver.BME280
        elif sensor_driver_as_str.lower() == "dht22":
            return SensorDriver.DHT22
        else:
            raise ValueError(f"Unsupported sensor driver: {sensor_driver_as_str}")

    def publish_sensor_data(self):
        id = uuid.uuid4()
        internal_sensor_data = self._internal_sensor.get_sensor_data()
        external_sensor_data = self._external_sensor.get_sensor_data()

        sensor_data_payload = SensorDataPayload(id=id, internal_sensor_data=internal_sensor_data, external_sensor_data=external_sensor_data)

        payload = sensor_data_payload.to_json()
        topic = self._mqtt_topic.sensor_data_topic
        self._mqtt_manager.publish(topic, payload)

from logging import Logger
from typing import Optional

from lib.domain.sensor_data import SensorData
from lib.mqtt.mqtt_topic import MqttTopic
from lib.sensor_drivers.sensor_driver import SensorDriver
from lib.sensor_drivers.sensor_factory import SensorFactory
from lib.mqtt.mqtt_manager import MQTTManager
from lib.sensor_drivers.sensor_interface import SensorInterface
from lib.util.digital_id import DigitalId


class EnviroSense:

    def __init__(self, logger: Logger, config: dict):
        self._logger = logger
        self._digital_id = DigitalId.create_digital_id()
        self._mqtt_topic = MqttTopic(self._digital_id)
        self._config = config

        self._control_app_logic = False
        self._sensor_app_logic = False

        self._sensor_driver = None
        self._mqtt_manager: Optional[MQTTManager] = None
        self._sensor: Optional[SensorInterface] = None

        self._initialize()
        self._running = True

    @property
    def digital_id(self):
        return self._digital_id

    def _initialize(self):
        self._set_application_logic()
        self._sensor_driver = self._set_driver()
        broker_address = self._config["enviro_sense"]["broker_address"]
        broker_port = self._config["enviro_sense"]["broker_port"]

        self._mqtt_manager = MQTTManager(broker_address=broker_address, port=broker_port, logger=self._logger)
        self._mqtt_manager.connect()

        self._sensor = SensorFactory.create_driver(self._sensor_driver)

    def _set_application_logic(self) -> None:
        self._control_app_logic = self._config["enviro_sense"]["control_app"]
        self._sensor_app_logic = self._config["enviro_sense"]["sensor_app"]

    def _set_driver(self) -> SensorDriver:
        driver = self._config["enviro_sense"]["sensor_driver"]
        if driver.lower() == "mock":
            return SensorDriver.MOCK
        elif driver.lower() == "bme280":
            return SensorDriver.BME280
        else:
            raise ValueError(f"Unsupported sensor driver: {driver}")

    def _sensor_application(self):
        temp = self._sensor.get_temperature()
        humidity = self._sensor.get_humidity()
        pressure = self._sensor.get_pressure()
        sensor_data = SensorData(temperature=temp,
                                 pressure=pressure,
                                 humidity=humidity)

        payload = sensor_data.to_json()
        topic = self._mqtt_topic.sensor_data_topic

        self._mqtt_manager.publish(topic, payload)

    def _control_application(self):
        pass

    def _shutdown(self):
        self._mqtt_manager.disconnect()

        self._mqtt_manager = None
        self._sensor = None

    def run(self):
        try:
            while self._running:
                self._sensor_application()
                self._control_application()
        except KeyboardInterrupt:
            self._logger.info("Shutting down gracefully...")
        finally:
            self.shutdown()

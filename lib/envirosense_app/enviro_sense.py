import time
from logging import Logger
from typing import Optional

from lib.envirosense_app.enviro_sense_sensor_application import EnviroSenseSensorApplication
from lib.mqtt.mqtt_manager import MQTTManager
from lib.util.digital_id import DigitalId
from lib.util.logger_factory import LoggerFactory


class EnviroSense:

    def __init__(self, config: dict):
        self._logger = LoggerFactory.create("EnviroSense")
        self._config = config

        self._digital_id = self._config["enviro_sense"]["sensor_digital_id"] or DigitalId.create_digital_id()
        self._mqtt_manager: Optional[MQTTManager] = None
        self._publish_sensor_data_timeout = self._config["enviro_sense"]["sensor_publish_data_timeout"] or 3
        self._initialize()
        self._running = True

    @property
    def digital_id(self):
        return self._digital_id

    def _initialize(self):
        broker_address = self._config["enviro_sense"]["broker_address"]
        broker_port = self._config["enviro_sense"]["broker_port"]

        self._mqtt_manager = MQTTManager(broker_address=broker_address, port=broker_port, logger=self._logger)
        self._mqtt_manager.connect()

        self._sensor_app = EnviroSenseSensorApplication(self._digital_id,
                                                        self._logger,
                                                        self._config["enviro_sense"]["internal_sensor_driver"],
                                                        self._config["enviro_sense"]["external_sensor_driver"],
                                                        self._mqtt_manager)

    def _shutdown(self):
        self._mqtt_manager.disconnect()
        self._mqtt_manager = None

    def run(self):
        try:
            while self._running:
                self._sensor_app.publish_sensor_data()
                time.sleep(self._publish_sensor_data_timeout) # we don't want to overrun our clients

        except KeyboardInterrupt:
            self._logger.info("Shutting down gracefully...")
        finally:
            self._shutdown()

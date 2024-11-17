import json
import time

from queue import Queue
from typing import Optional

from lib.controllers.enviroment_controller import EnvironmentController
from lib.domain.room_control_data import RoomControlData
from lib.domain.sensor_data import SensorData
from lib.gpio.relay_driver import RelayDriver
from lib.gpio.relay_factory import RelayFactory
from lib.mqtt.mqtt_manager import MQTTManager
from lib.mqtt.mqtt_topic import MqttTopic
from lib.util.csv_lookup import CSVLookup
from lib.util.digital_id import DigitalId
from lib.util.logger_factory import LoggerFactory


class EnviroControl:

    def __init__(self, config: dict) -> None:
        self._logger = LoggerFactory.create("EnviroControl")
        self._config = config

        self._csv_env_table = CSVLookup("doc/waterdampspanning.csv")

        self._gpio_pin_1 = self._config["enviro_sense"]["control_relay_gpio_1"] or 17
        self._gpio_pin_2 = self._config["enviro_sense"]["control_relay_gpio_2"] or 27

        self._kp_heater = self._config["enviro_sense"]["kp_heater"] or 0.3
        self._kd_heater = self._config["enviro_sense"]["kd_heater"] or 0.2
        self._threshold_heater = self._config["enviro_sense"]["threshold_heater"] or 0.5

        self._kp_steamer = self._config["enviro_sense"]["kp_steamer"] or 0.3
        self._kd_steamer = self._config["enviro_sense"]["kd_steamer"] or 0.2
        self._threshold_steamer = self._config["enviro_sense"]["threshold_steamer"] or 0.5

        self._digital_id = self._config["enviro_sense"]["sensor_digital_id"] or DigitalId.create_digital_id()
        self._publish_sensor_data_timeout = self._config["enviro_sense"]["sensor_publish_data_timeout"] or 3

        self._sensor_data_queue = Queue()  # we are going to use this as a fifo data structure (queue)

        self._relay_driver = self._set_relay_driver(self._config["enviro_sense"]["relay_driver"])
        self._heating_element = RelayFactory.create_relay(self._relay_driver, self._gpio_pin_1)
        self._steam_element = RelayFactory.create_relay(self._relay_driver, self._gpio_pin_2)

        self._mqtt_manager: Optional[MQTTManager] = None
        self._initialize_mqtt()

        self._heating_control = EnvironmentController(self._kp_heater, self._kd_heater, self._threshold_heater)
        self._steamer_control = EnvironmentController(self._kp_steamer, self._kd_steamer, self._threshold_steamer)

        self._running = True
        self._logger.info("envirocontrol has been init")

    @property
    def digital_id(self) -> str:
        return self._digital_id

    def _initialize_mqtt(self) -> None:
        broker_address = self._config["enviro_sense"]["broker_address"]
        broker_port = self._config["enviro_sense"]["broker_port"]

        self._mqtt_topic = MqttTopic(self._digital_id)
        self._mqtt_manager = MQTTManager(broker_address=broker_address,
                                         port=broker_port,
                                         logger=self._logger,
                                         message_list=self._sensor_data_queue)
        self._mqtt_manager.connect()
        time.sleep(2)
        self._mqtt_manager.subscribe(self._mqtt_topic.sensor_data_topic)

    def _set_relay_driver(self, relay_driver_as_str: str) -> RelayDriver:
        if relay_driver_as_str.lower() == "mock":
            return RelayDriver.MOCK
        elif relay_driver_as_str.lower() == "rpi":
            return RelayDriver.RPI
        else:
            raise ValueError(f"Unsupported sensor driver: {relay_driver_as_str}")

    def _shutdown(self) -> None:
        self._mqtt_manager.disconnect()
        self._mqtt_manager = None

    def _handle_sensor_data_message(self, data: dict) -> None:
        if data is None:
            return

        self._logger.info(f"received this sensor data {data}")

        data_as_dict = json.loads(data["payload"])
        internal_sensor_data = SensorData.to_sensor_data(data_as_dict["internal_sensor_data"])
        external_sensor_data = SensorData.to_sensor_data(data_as_dict["external_sensor_data"])

        self._handle_heater(external_sensor_data, internal_sensor_data)
        self._handle_steamer(internal_sensor_data)

    def _handle_steamer(self, internal_sensor_data: SensorData) -> None:
        # stel u heersende temperatuur is 30° dan gaat ge in u tabel de waarde zoeken voor de temperatuur van 29° wat dat is het maximale vocht dat er mag zijn
        # is dat onder die waarde van 29° dan moet ge de stomer gaan aanzetten
        temp = internal_sensor_data.temperature - 1
        target_humidity = self._csv_env_table.get_closest_value(temp)[1]
        if target_humidity is None:
            return

        turn_steamer_on = self._steamer_control.calculate_abstract_device_on_off(internal_sensor_data.humidity, target_humidity)
        if turn_steamer_on:
            self._steam_element.close_relay()
        else:
            self._steam_element.open_relay()

    def _handle_heater(self, external_sensor_data: SensorData, internal_sensor_data: SensorData) -> None:
        # Is het buiten warmer dan binnen moet het verwarmingselement inschakelen tot de warmte binnen hoger
        turn_heater_on = self._heating_control.calculate_abstract_device_on_off(internal_sensor_data.temperature, external_sensor_data.temperature)
        if turn_heater_on:
            self._heating_element.close_relay()
        else:
            self._heating_element.open_relay()

    def _handle_heater_data(self, data: dict) -> None:
        room_control_data = RoomControlData.to_sensor_data(data["payload"])
        if room_control_data is None:
            return
        self._kp_heater = room_control_data.kp
        self._kd_heater = room_control_data.kd
        self._threshold_heater = room_control_data.threshold
        self._heating_control = EnvironmentController(self._kp_heater, self._kd_heater, self._threshold_heater)

    def _handle_steamer_data(self, data: dict) -> None:
        room_control_data = RoomControlData.to_sensor_data(data["payload"])
        if room_control_data is None:
            return
        self._kp_steamer = room_control_data.kp
        self._kd_steamer = room_control_data.kd
        self._threshold_steamer = room_control_data.threshold
        self._steamer_control = EnvironmentController(self._kp_steamer, self._kd_steamer, self._threshold_steamer)

    def run(self) -> None:
        """
        Start with Kp: Begin with a low Kp and gradually increase until you see a good response without oscillations.
        Adjust Kd: Increase Kd to reduce overshoot or oscillations if they appear.
        """
        self._heating_element.open_relay()
        self._steam_element.open_relay()

        try:
            while self._running:
                if not self._sensor_data_queue.empty():
                    data = self._sensor_data_queue.get()

                    if data["topic"] == self._mqtt_topic.sensor_data_topic:
                        self._handle_sensor_data_message(data)

                    if data["topic"] == self._mqtt_topic.set_heater_values:
                        self._handle_heater_data(data)

                    if data["topic"] == self._mqtt_topic.set_steamer_values:
                        self._handle_steamer_data(data)

        except KeyboardInterrupt:
            self._logger.info("Shutting down gracefully...")
        finally:
            self._shutdown()

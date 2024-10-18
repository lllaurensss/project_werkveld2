import time

from queue import Queue
from typing import Optional
from simple_pid import PID

from lib.domain.room_control_data import RoomControlData
from lib.domain.sensor_data import SensorData
from lib.gpio.relay_driver import RelayDriver
from lib.gpio.relay_factory import RelayFactory
from lib.mqtt.mqtt_manager import MQTTManager
from lib.mqtt.mqtt_topic import MqttTopic
from lib.util.digital_id import DigitalId
from lib.util.logger_factory import LoggerFactory


class EnviroControl:

    def __init__(self, config: dict):
        self._logger = LoggerFactory.create("EnviroControl")
        self._config = config

        self._desired_temp = self._config["enviro_sense"]["desired_temp"] or 20
        self._gpio_pin_1 = self._config["enviro_sense"]["control_relay_gpio_1"] or 17
        self._gpio_pin_2 = self._config["enviro_sense"]["control_relay_gpio_2"] or 27
        self._kp = self._config["enviro_sense"]["kp"] or 1.0
        self._kd = self._config["enviro_sense"]["kd"] or 0.05
        self._ki = 0  # we are going to use a pd controller
        self._digital_id = self._config["enviro_sense"]["sensor_digital_id"] or DigitalId.create_digital_id()
        self._publish_sensor_data_timeout = self._config["enviro_sense"]["sensor_publish_data_timeout"] or 3

        self._sensor_data_queue = Queue()  # we are going to use this as a fifo data structure (queue)

        self._relay_driver = self._set_relay_driver(self._config["enviro_sense"]["relay_driver"])
        self._relay_1 = RelayFactory.create_relay(self._relay_driver, self._gpio_pin_1)
        self._relay_2 = RelayFactory.create_relay(self._relay_driver, self._gpio_pin_2)

        self._mqtt_manager: Optional[MQTTManager] = None
        self._initialize_mqtt()

        self._pid = None
        self._initialize_pid()

        self._running = True

    @property
    def digital_id(self):
        return self._digital_id

    def _initialize_mqtt(self):
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

    def _initialize_pid(self):
        self._pid = PID(self._kp, self._ki, self._kd, setpoint=self._desired_temp)  # Ki is set to 0 for PD control
        self._pid.output_limits = (0, 1)

    def _set_relay_driver(self, relay_driver_as_str: str) -> RelayDriver:
        if relay_driver_as_str.lower() == "mock":
            return RelayDriver.MOCK
        elif relay_driver_as_str.lower() == "rpi":
            return RelayDriver.RPI
        else:
            raise ValueError(f"Unsupported sensor driver: {relay_driver_as_str}")

    def _shutdown(self):
        self._mqtt_manager.disconnect()
        self._mqtt_manager = None

    def run(self):
        """
        Start with Kp: Begin with a low Kp and gradually increase until you see a good response without oscillations.
        Adjust Kd: Increase Kd to reduce overshoot or oscillations if they appear.
        """
        try:
            while self._running:
                if not self._sensor_data_queue.empty():
                    data = self._sensor_data_queue.get()

                    if data["topic"] == self._mqtt_topic.sensor_data_topic:
                        sensor_data = SensorData.to_sensor_data(data["payload"])
                        if sensor_data is None:
                            return

                        self._logger.info(f"received this sensor data {sensor_data}")

                        current_temperature = sensor_data.temperature
                        pid_output = self._pid(current_temperature)

                        # Relay control: 1 -> heater on, 0 -> heater off
                        if pid_output >= 0.5:  # Threshold can be tuned
                            self._relay_1.close_relay()
                            self._relay_2.close_relay()
                        else:
                            # heater_off()
                            self._relay_1.open_relay()
                            self._relay_2.open_relay()

                        self._logger.info(f"Temperature: {current_temperature:.2f}°C, Heater Status: {'ON' if pid_output >= 0.5 else 'OFF'}")
                        time.sleep(1)

                    if data["topic"] == self._mqtt_topic.set_desired_temp:
                        room_control_data = RoomControlData(**data["payload"])
                        self._desired_temp = room_control_data.temperature

        except KeyboardInterrupt:
            self._logger.info("Shutting down gracefully...")
        finally:
            self._shutdown()

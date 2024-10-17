from enum import Enum


class MqttTopic:

    def __init__(self, digital_id: str) -> None:
        self._sensor_data_topic = f"/{digital_id}/sensor_data/"
        self._control_desired_temp = f"/{digital_id}/set_desired_temp"

    @property
    def sensor_data_topic(self):
        return self._sensor_data_topic
    
    @property
    def set_desired_temp(self):
        return self._control_desired_temp
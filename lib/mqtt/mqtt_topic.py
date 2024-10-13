from enum import Enum


class MqttTopic:

    def __init__(self, digital_id: str) -> None:
        self._sensor_data_topic = f"/{digital_id}/sensor_data/"

    @property
    def sensor_data_topic(self):
        return self._sensor_data_topic
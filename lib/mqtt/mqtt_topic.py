from enum import Enum


class MqttTopic:

    def __init__(self, digital_id: str) -> None:
        self._internal_sensor_data_topic = f"/{digital_id}/sensor_data/"
        self._set_heater_values = f"/{digital_id}/set_heater_values/"
        self._set_steamer_values = f"/{digital_id}/set_steamer_values/"

    @property
    def sensor_data_topic(self):
        return self._internal_sensor_data_topic


    @property
    def set_heater_values(self):
        return self._set_heater_values

    @property
    def set_steamer_values(self):
        return self._set_steamer_values

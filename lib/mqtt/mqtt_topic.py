from enum import Enum


class MqttTopic(Enum):
    sensor_data_topic = "/{digital_id}/sensor_data/"

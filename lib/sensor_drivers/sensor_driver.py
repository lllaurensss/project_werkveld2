from enum import Enum


class SensorDriver(Enum):
    MOCK = "MOCK"
    BME280 = "BME280"
    DHT22 = "DHT22"

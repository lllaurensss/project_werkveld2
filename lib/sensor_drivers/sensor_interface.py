class SensorInterface:

    def setup(self, mode="normal", temperature_oversampling=16, pressure_oversampling=16, humidity_oversampling=16, temperature_standby=500) -> None:
        pass

    def get_temperature(self) -> float:
        pass

    def get_pressure(self) -> float:
        pass

    def get_humidity(self) -> float:
        pass

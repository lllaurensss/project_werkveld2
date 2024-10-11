import json
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class SensorData:
    temperature: float = field(default=0.0)
    humidity: float = field(default=0.0)
    pressure: float = field(default=1013.25)  # Standard sea-level atmospheric pressure in hPa
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        # Validate ranges for realistic data
        if not (-50.0 <= self.temperature <= 50.0):
            raise ValueError(f"Temperature out of range: {self.temperature}°C")
        if not (0.0 <= self.humidity <= 100.0):
            raise ValueError(f"Humidity out of range: {self.humidity}%")
        if not (800.0 <= self.pressure <= 1200.0):
            raise ValueError(f"Pressure out of range: {self.pressure} hPa")

    def to_json(self):
        return json.dumps(asdict(self), default=str)

    def __str__(self):
        return (f"SensorData(Temperature: {self.temperature}°C, "
                f"Humidity: {self.humidity}%, Pressure: {self.pressure} hPa, "
                f"Timestamp: {self.timestamp.isoformat()})")

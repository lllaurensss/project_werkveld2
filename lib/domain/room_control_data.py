import json
from dataclasses import dataclass, field, asdict


@dataclass
class RoomControlData:
    temperature: float = field(default=0.0)

    def __post_init__(self):
        # Validate ranges for realistic data
        if not (-100.0 <= self.temperature <= 100.0):
            raise ValueError(f"Temperature out of range: {self.temperature}°C")

    def to_json(self):
        return json.dumps(asdict(self), default=str)
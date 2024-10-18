import json
from dataclasses import dataclass, field, asdict


@dataclass
class RoomControlData:
    temperature: float = field(default=0.0)
    kp: float = field(default=1.0)
    kd: float = field(default=0.005)

    def __post_init__(self):
        # Validate ranges for realistic data
        if not (-100.0 <= self.temperature <= 100.0):
            raise ValueError(f"Temperature out of range: {self.temperature}°C")

    def to_json(self):
        return json.dumps(asdict(self), default=str)

    @staticmethod
    def to_sensor_data(json_str: str) -> 'RoomControlData':
        try:
            data = json.loads(json_str)

            return RoomControlData(
                temperature=data['temperature'],
                kp=data['kp'],
                kd=data['kd']
            )
        except Exception as e:
            return None

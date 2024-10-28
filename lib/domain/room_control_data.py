import json
from dataclasses import dataclass, field, asdict


@dataclass
class RoomControlData:
    kp: float = field(default=1.0)
    kd: float = field(default=0.005)

    def to_json(self):
        return json.dumps(asdict(self), default=str)

    @staticmethod
    def to_sensor_data(json_str: str) -> 'RoomControlData':
        try:
            data = json.loads(json_str)

            return RoomControlData(
                kp=data['kp'],
                kd=data['kd']
            )

        except Exception as e:
            return None

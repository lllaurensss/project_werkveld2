import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from uuid import UUID
from lib.domain.sensor_data import SensorData


@dataclass
class SensorDataPayload:
    id: UUID
    internal_sensor_data: SensorData
    external_sensor_data: SensorData
    timestamp: datetime = field(default_factory=datetime.now)

    def to_json(self):
        return json.dumps(asdict(self), default=str)
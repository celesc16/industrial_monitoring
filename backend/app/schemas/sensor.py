from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


SensorConnectionStatus = Literal["online", "offline", "inactive"]


class SensorLatestReading(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    temperature: float
    vibration: float
    pressure: float
    prediction: int
    is_anomaly: bool
    anomaly_score: float


class SensorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    location: str
    description: str | None

    is_active: bool
    connection_status: SensorConnectionStatus
    last_seen_at: datetime | None

    created_at: datetime
    updated_at: datetime

    latest_reading: SensorLatestReading | None
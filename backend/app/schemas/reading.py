from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SensorReadingIn(BaseModel):
    sensor_id: str
    temperature: float
    vibration: float
    pressure: float


class ReadingOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    timestamp: datetime
    sensor_id: str
    temperature: float
    vibration: float
    pressure: float
    prediction: int
    is_anomaly: bool
    anomaly_score: float


class LatestReading(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    sensor_id: str
    temperature: float
    vibration: float
    pressure: float
    is_anomaly: bool
    timestamp: datetime


class StatsOut(BaseModel):
    total_readings: int
    total_anomalies: int
    anomalies_last_24h: int
    latest_reading: LatestReading | None = None


class PaginationOut(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class ReadingsPageOut(BaseModel):
    items: list[ReadingOut]
    pagination: PaginationOut
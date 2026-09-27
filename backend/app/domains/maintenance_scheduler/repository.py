from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.exceptions import SensorNotFoundError
from app.models.reading import Reading
from app.models.sensor import Sensor

SECONDS_PER_DAY = 86_400.0


@dataclass
class SensorUsageHistory:
    sensor_id: str
    span_days: float
    anomaly_count: int
    failure_intervals_days: list[float]


class MaintenanceRepository:
    """Data access for the maintenance scheduler domain."""

    def __init__(self, db: Session):
        self._db = db

    def get_usage_history(self, sensor_id: str) -> SensorUsageHistory:
        if self._db.get(Sensor, sensor_id) is None:
            raise SensorNotFoundError(sensor_id)

        readings = (
            self._db.query(Reading)
            .filter(Reading.sensor_id == sensor_id)
            .order_by(Reading.timestamp.asc())
            .all()
        )

        timestamps = [reading.timestamp for reading in readings]
        anomaly_timestamps = [
            reading.timestamp
            for reading in readings
            if reading.is_anomaly
        ]

        if timestamps:
            span_days = max(
                (timestamps[-1] - timestamps[0]).total_seconds()
                / SECONDS_PER_DAY,
                0.0,
            )
        else:
            span_days = 0.0

        failure_intervals_days = [
            (right - left).total_seconds() / SECONDS_PER_DAY
            for left, right in zip(
                anomaly_timestamps,
                anomaly_timestamps[1:],
            )
            if right > left
        ]

        return SensorUsageHistory(
            sensor_id=sensor_id,
            span_days=span_days,
            anomaly_count=len(anomaly_timestamps),
            failure_intervals_days=failure_intervals_days,
        )
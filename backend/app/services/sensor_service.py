from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.reading import Reading
from app.models.sensor import Sensor


def get_connection_status(sensor: Sensor) -> str:
    if not sensor.is_active:
        return "inactive"

    if sensor.last_seen_at is None:
        return "offline"

    offline_limit = datetime.utcnow() - timedelta(
        seconds=settings.sensor_offline_seconds
    )

    if sensor.last_seen_at < offline_limit:
        return "offline"

    return "online"


def get_latest_reading(
    db: Session,
    sensor_id: str,
) -> Reading | None:
    return (
        db.query(Reading)
        .filter(Reading.sensor_id == sensor_id)
        .order_by(Reading.timestamp.desc())
        .first()
    )


def serialize_sensor(
    db: Session,
    sensor: Sensor,
) -> dict:
    latest_reading = get_latest_reading(db, sensor.id)

    return {
        "id": sensor.id,
        "name": sensor.name,
        "location": sensor.location,
        "description": sensor.description,
        "is_active": sensor.is_active,
        "connection_status": get_connection_status(sensor),
        "last_seen_at": sensor.last_seen_at,
        "created_at": sensor.created_at,
        "updated_at": sensor.updated_at,
        "latest_reading": latest_reading,
    }
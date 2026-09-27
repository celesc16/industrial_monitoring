from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.reading import Reading
from app.models.sensor import Sensor
from app.services.sensor_service import (
    get_connection_status,
    get_latest_reading,
    serialize_sensor,
)


def _build_sensor(
    is_active: bool = True,
    last_seen_at: datetime | None = None,
) -> Sensor:
    return Sensor(
        id="SENSOR-001",
        name="Motor principal",
        location="Línea de producción A",
        description="Motor principal",
        is_active=is_active,
        last_seen_at=last_seen_at,
    )


class TestGetConnectionStatus:
    def test_inactive_sensor_is_inactive(self):
        sensor = _build_sensor(is_active=False)

        assert get_connection_status(sensor) == "inactive"

    def test_active_sensor_without_last_seen_is_offline(self):
        sensor = _build_sensor(is_active=True, last_seen_at=None)

        assert get_connection_status(sensor) == "offline"

    def test_active_sensor_with_recent_activity_is_online(self):
        sensor = _build_sensor(
            is_active=True,
            last_seen_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        assert get_connection_status(sensor) == "online"

    def test_active_sensor_with_stale_activity_is_offline(self):
        stale = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
            seconds=settings.sensor_offline_seconds + 1
        )
        sensor = _build_sensor(is_active=True, last_seen_at=stale)

        assert get_connection_status(sensor) == "offline"


class TestGetLatestReading:
    def test_returns_none_without_readings(self, db):
        assert get_latest_reading(db, "SENSOR-001") is None

    def test_returns_newest_reading(self, db):
        older = Reading(
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=5),
            sensor_id="SENSOR-001",
            temperature=60.0,
            vibration=1.5,
            pressure=100.0,
            prediction=1,
            is_anomaly=False,
            anomaly_score=0.1,
        )
        newer = Reading(
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            sensor_id="SENSOR-001",
            temperature=62.0,
            vibration=1.8,
            pressure=102.0,
            prediction=1,
            is_anomaly=False,
            anomaly_score=0.2,
        )
        other_sensor = Reading(
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            sensor_id="SENSOR-002",
            temperature=50.0,
            vibration=1.0,
            pressure=90.0,
            prediction=1,
            is_anomaly=False,
            anomaly_score=0.0,
        )
        db.add_all([older, newer, other_sensor])
        db.commit()

        latest = get_latest_reading(db, "SENSOR-001")

        assert latest is not None
        assert latest.temperature == 62.0


class TestSerializeSensor:
    def test_serialize_without_readings(self, db):
        sensor = db.get(Sensor, "SENSOR-001")
        data = serialize_sensor(db, sensor)

        assert data["id"] == "SENSOR-001"
        assert data["name"] == "Motor principal"
        assert data["is_active"] is True
        assert data["connection_status"] in {"online", "offline", "inactive"}
        assert data["last_seen_at"] is None
        assert data["latest_reading"] is None

    def test_serialize_includes_latest_reading(self, db):
        db.add(
            Reading(
                timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                sensor_id="SENSOR-001",
                temperature=80.0,
                vibration=3.0,
                pressure=120.0,
                prediction=-1,
                is_anomaly=True,
                anomaly_score=-0.42,
            )
        )
        db.commit()

        sensor = db.get(Sensor, "SENSOR-001")
        data = serialize_sensor(db, sensor)

        assert data["latest_reading"] is not None
        assert data["latest_reading"].temperature == 80.0
        assert data["latest_reading"].is_anomaly is True
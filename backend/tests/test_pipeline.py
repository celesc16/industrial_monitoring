import asyncio
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import (
    InactiveSensorError,
    SensorNotFoundError,
)
from app.models.sensor import Sensor
from app.services import pipeline


class FakeDetector:
    """Detector determinístico para aislar el pipeline del modelo real."""

    def __init__(self, is_anomaly: bool = False):
        self.is_anomaly = is_anomaly

    def predict(self, reading: dict) -> dict:
        return {
            "prediction": -1 if self.is_anomaly else 1,
            "is_anomaly": self.is_anomaly,
            "anomaly_score": -0.42 if self.is_anomaly else 0.42,
        }


@pytest.fixture
def patched_pipeline(monkeypatch, session_factory):
    monkeypatch.setattr(pipeline, "SessionLocal", session_factory)
    telegram_send = AsyncMock(return_value=False)
    broadcast = AsyncMock(return_value=None)
    monkeypatch.setattr(pipeline, "send_telegram_alert", telegram_send)
    monkeypatch.setattr(pipeline.manager, "broadcast", broadcast)
    return telegram_send, broadcast


def _run(coro):
    return asyncio.run(coro)


class TestProcessReadingErrors:
    def test_unknown_sensor_raises(self, db, patched_pipeline):
        payload = {
            "sensor_id": "NO-EXISTE",
            "temperature": 60.0,
            "vibration": 1.5,
            "pressure": 100.0,
        }

        with pytest.raises(SensorNotFoundError):
            _run(pipeline.process_reading(payload, FakeDetector()))

    def test_inactive_sensor_raises(self, db, patched_pipeline):
        sensor = db.get(Sensor, "SENSOR-001")
        sensor.is_active = False
        db.commit()

        payload = {
            "sensor_id": "SENSOR-001",
            "temperature": 60.0,
            "vibration": 1.5,
            "pressure": 100.0,
        }

        with pytest.raises(InactiveSensorError):
            _run(pipeline.process_reading(payload, FakeDetector()))


class TestProcessReadingSuccess:
    def test_normal_reading_is_persisted(self, db, patched_pipeline):
        _, broadcast = patched_pipeline

        record = _run(
            pipeline.process_reading(
                {
                    "sensor_id": "SENSOR-001",
                    "temperature": 60.0,
                    "vibration": 1.5,
                    "pressure": 100.0,
                },
                FakeDetector(is_anomaly=False),
            )
        )

        assert record["sensor_id"] == "SENSOR-001"
        assert record["is_anomaly"] is False
        assert record["prediction"] == 1
        assert isinstance(record["id"], int)

        broadcast.assert_awaited_once()

        sensor = db.get(Sensor, "SENSOR-001")
        assert sensor.last_seen_at is not None

    def test_anomalous_reading_sends_telegram_alert(
        self, db, patched_pipeline
    ):
        telegram_send, _ = patched_pipeline

        record = _run(
            pipeline.process_reading(
                {
                    "sensor_id": "SENSOR-001",
                    "temperature": 160.0,
                    "vibration": 20.0,
                    "pressure": 400.0,
                },
                FakeDetector(is_anomaly=True),
            )
        )

        assert record["is_anomaly"] is True
        assert record["prediction"] == -1
        telegram_send.assert_awaited_once()

    def test_reading_queryable_in_new_session(
        self, db, session_factory, patched_pipeline
    ):
        _run(
            pipeline.process_reading(
                {
                    "sensor_id": "SENSOR-001",
                    "temperature": 61.0,
                    "vibration": 1.6,
                    "pressure": 101.0,
                },
                FakeDetector(),
            )
        )

        check_session = session_factory()
        try:
            from app.models.reading import Reading

            reading = (
                check_session.query(Reading)
                .filter(Reading.sensor_id == "SENSOR-001")
                .first()
            )
            assert reading is not None
            assert reading.temperature == 61.0
        finally:
            check_session.close()
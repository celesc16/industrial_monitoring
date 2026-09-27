from datetime import datetime, timedelta, timezone

from app.models.reading import Reading


def _add_readings(db) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(hours=50)
    db.add_all([
        Reading(
            timestamp=now,
            sensor_id="SENSOR-001",
            temperature=60.0,
            vibration=1.5,
            pressure=100.0,
            prediction=1,
            is_anomaly=False,
            anomaly_score=0.2,
        ),
        Reading(
            timestamp=now - timedelta(hours=1),
            sensor_id="SENSOR-001",
            temperature=92.0,
            vibration=4.0,
            pressure=140.0,
            prediction=-1,
            is_anomaly=True,
            anomaly_score=-0.4,
        ),
        Reading(
            timestamp=old,
            sensor_id="SENSOR-002",
            temperature=90.0,
            vibration=5.0,
            pressure=150.0,
            prediction=-1,
            is_anomaly=True,
            anomaly_score=-0.5,
        ),
    ])
    db.commit()


class TestStats:
    def test_empty_db(self, client):
        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        body = response.json()
        assert body["total_readings"] == 0
        assert body["total_anomalies"] == 0
        assert body["anomalies_last_24h"] == 0
        assert body["latest_reading"] is None

    def test_counts(self, client, db):
        _add_readings(db)

        response = client.get("/api/v1/stats")

        assert response.status_code == 200
        body = response.json()
        assert body["total_readings"] == 3
        assert body["total_anomalies"] == 2
        assert body["anomalies_last_24h"] == 1
        assert body["latest_reading"]["sensor_id"] == "SENSOR-001"
        assert body["latest_reading"]["is_anomaly"] is False

    def test_filtered_by_sensor(self, client, db):
        _add_readings(db)

        response = client.get(
            "/api/v1/stats", params={"sensor_id": "SENSOR-002"}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total_readings"] == 1
        assert body["total_anomalies"] == 1
        assert body["anomalies_last_24h"] == 0
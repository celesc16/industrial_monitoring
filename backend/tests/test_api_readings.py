from datetime import datetime, timedelta, timezone

from app.models.reading import Reading


def _add_readings(db) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
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
            timestamp=now - timedelta(minutes=1),
            sensor_id="SENSOR-001",
            temperature=92.0,
            vibration=4.0,
            pressure=140.0,
            prediction=-1,
            is_anomaly=True,
            anomaly_score=-0.4,
        ),
        Reading(
            timestamp=now - timedelta(minutes=2),
            sensor_id="SENSOR-002",
            temperature=55.0,
            vibration=1.0,
            pressure=90.0,
            prediction=1,
            is_anomaly=False,
            anomaly_score=0.1,
        ),
    ])
    db.commit()


class TestGetReadings:
    def test_empty_db(self, client):
        response = client.get("/api/v1/readings")

        assert response.status_code == 200
        body = response.json()
        assert body["items"] == []
        assert body["pagination"]["total_items"] == 0
        assert body["pagination"]["total_pages"] == 0

    def test_returns_readings_sorted_desc(self, client, db):
        _add_readings(db)

        response = client.get("/api/v1/readings")

        assert response.status_code == 200
        body = response.json()
        assert body["pagination"]["total_items"] == 3
        timestamps = [item["timestamp"] for item in body["items"]]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_filters_by_sensor(self, client, db):
        _add_readings(db)

        response = client.get(
            "/api/v1/readings", params={"sensor_id": "SENSOR-002"}
        )

        body = response.json()
        assert body["pagination"]["total_items"] == 1
        assert body["items"][0]["sensor_id"] == "SENSOR-002"

    def test_filters_by_anomaly(self, client, db):
        _add_readings(db)

        response = client.get(
            "/api/v1/readings", params={"is_anomaly": "true"}
        )

        body = response.json()
        assert body["pagination"]["total_items"] == 1
        assert body["items"][0]["is_anomaly"] is True

    def test_filters_by_date_range(self, client, db):
        _add_readings(db)
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        response = client.get(
            "/api/v1/readings",
            params={
                "date_from": (now - timedelta(minutes=1, seconds=30)).isoformat()
            },
        )

        body = response.json()
        assert body["pagination"]["total_items"] == 2

    def test_pages(self, client, db):
        _add_readings(db)

        response = client.get(
            "/api/v1/readings", params={"page": 2, "page_size": 2}
        )

        body = response.json()
        assert body["pagination"]["page"] == 2
        assert len(body["items"]) == 1

    def test_invalid_page_rejected(self, client):
        assert client.get(
            "/api/v1/readings", params={"page": 0}
        ).status_code == 422

    def test_invalid_page_size_rejected(self, client):
        assert client.get(
            "/api/v1/readings", params={"page_size": 1000}
        ).status_code == 422

    def test_reading_shape(self, client, db):
        _add_readings(db)

        item = client.get("/api/v1/readings").json()["items"][0]
        assert set(item.keys()) == {
            "id",
            "timestamp",
            "sensor_id",
            "temperature",
            "vibration",
            "pressure",
            "prediction",
            "is_anomaly",
            "anomaly_score",
        }


class TestExportReadingsCsv:
    def test_returns_csv_with_attachment_header(self, client, db):
        _add_readings(db)

        response = client.get("/api/v1/readings/export")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/csv")
        assert "attachment" in response.headers["content-disposition"]
        assert response.headers["content-disposition"].startswith(
            'attachment; filename="lecturas_industriales_'
        )

    def test_csv_contains_rows(self, client, db):
        _add_readings(db)

        content = client.get("/api/v1/readings/export").text

        assert "Fecha;Hora;Sensor" in content
        assert "SENSOR-001" in content
        assert "SENSOR-002" in content

    def test_empty_export_has_only_header(self, client):
        content = client.get("/api/v1/readings/export").text

        lines = content.strip().splitlines()
        assert len(lines) == 1
        assert lines[0].startswith("\ufeffFecha;Hora;Sensor")
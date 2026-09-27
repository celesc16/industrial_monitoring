from app.models.sensor import Sensor

VALID_PAYLOAD = {
    "sensor_id": "SENSOR-001",
    "temperature": 60.0,
    "vibration": 1.5,
    "pressure": 100.0,
}


class TestSimulateReading:
    def test_success_returns_reading(self, client):
        response = client.post("/api/v1/simulate", json=VALID_PAYLOAD)

        assert response.status_code == 200
        body = response.json()
        assert body["sensor_id"] == "SENSOR-001"
        assert isinstance(body["id"], int)
        assert "is_anomaly" in body
        assert "anomaly_score" in body

    def test_unknown_sensor_returns_404(self, client):
        response = client.post(
            "/api/v1/simulate",
            json={**VALID_PAYLOAD, "sensor_id": "NO-EXISTE"},
        )

        assert response.status_code == 404
        assert "no está registrado" in response.json()["detail"]

    def test_inactive_sensor_returns_409(self, client, db):
        sensor = db.get(Sensor, "SENSOR-001")
        sensor.is_active = False
        db.commit()

        response = client.post("/api/v1/simulate", json=VALID_PAYLOAD)

        assert response.status_code == 409
        assert "desactivado" in response.json()["detail"]

    def test_missing_required_field_returns_422(self, client):
        response = client.post(
            "/api/v1/simulate", json={"sensor_id": "SENSOR-001"}
        )

        assert response.status_code == 422

    def test_reading_persisted_in_db(self, client, db):
        response = client.post("/api/v1/simulate", json=VALID_PAYLOAD)

        sensor = db.get(Sensor, "SENSOR-001")
        assert sensor.last_seen_at is not None
        assert response.status_code == 200
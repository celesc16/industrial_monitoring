from app.models.sensor import Sensor

SIMULATE_URL = "/api/v1/simulate"

VALID_PAYLOAD = {
    "sensor_id": "SENSOR-001",
    "temperature": 60.0,
    "vibration": 1.5,
    "pressure": 100.0,
}


class TestSimulateReading:
    def test_success_returns_reading(self, client, auth):
        response = client.post(
            SIMULATE_URL,
            json=VALID_PAYLOAD,
            headers=auth(),
        )

        assert response.status_code == 200
        body = response.json()
        assert body["sensor_id"] == "SENSOR-001"
        assert isinstance(body["id"], int)
        assert "is_anomaly" in body
        assert "anomaly_score" in body

    def test_unknown_sensor_returns_404(self, client, auth):
        response = client.post(
            SIMULATE_URL,
            json={**VALID_PAYLOAD, "sensor_id": "NO-EXISTE"},
            headers=auth(),
        )

        assert response.status_code == 404
        assert "no está registrado" in response.json()["detail"]

    def test_inactive_sensor_returns_409(self, client, db, auth):
        sensor = db.get(Sensor, "SENSOR-001")
        sensor.is_active = False
        db.commit()

        response = client.post(
            SIMULATE_URL,
            json=VALID_PAYLOAD,
            headers=auth(),
        )

        assert response.status_code == 409
        assert "desactivado" in response.json()["detail"]

    def test_missing_required_field_returns_422(self, client, auth):
        response = client.post(
            SIMULATE_URL,
            json={"sensor_id": "SENSOR-001"},
            headers=auth(),
        )

        assert response.status_code == 422

    def test_reading_persisted_in_db(self, client, db, auth):
        response = client.post(
            SIMULATE_URL,
            json=VALID_PAYLOAD,
            headers=auth(),
        )

        sensor = db.get(Sensor, "SENSOR-001")
        assert sensor.last_seen_at is not None
        assert response.status_code == 200

    def test_requires_authentication(self, client):
        response = client.post(SIMULATE_URL, json=VALID_PAYLOAD)

        assert response.status_code == 401

    def test_rejects_invalid_token(self, client):
        response = client.post(
            SIMULATE_URL,
            json=VALID_PAYLOAD,
            headers={"Authorization": "Bearer token-invalido"},
        )

        assert response.status_code == 401

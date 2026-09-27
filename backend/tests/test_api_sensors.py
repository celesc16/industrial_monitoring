"""Tests of the sensor endpoints."""

from unittest.mock import AsyncMock

from app.models.sensor import Sensor


class TestGetSensors:
    def test_returns_seeded_sensors(self, client):
        response = client.get("/api/v1/sensors")

        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_sensor_shape(self, client):
        response = client.get("/api/v1/sensors")

        sensor = response.json()[0]
        assert set(sensor.keys()) == {
            "id",
            "name",
            "location",
            "description",
            "is_active",
            "connection_status",
            "last_seen_at",
            "created_at",
            "updated_at",
            "latest_reading",
        }


class TestGetSensor:
    def test_get_existing_sensor(self, client):
        response = client.get("/api/v1/sensors/SENSOR-001")

        assert response.status_code == 200
        assert response.json()["id"] == "SENSOR-001"

    def test_get_unknown_sensor_returns_404(self, client):
        response = client.get("/api/v1/sensors/NO-EXISTE")

        assert response.status_code == 404
        assert "no está registrado" in response.json()["detail"]


class TestUpdateSensorStatus:
    def _mock_telegram(self, monkeypatch):
        telegram_send = AsyncMock(return_value=False)
        monkeypatch.setattr(
            "app.api.v1.endpoints.sensors.send_telegram_alert",
            telegram_send,
        )
        return telegram_send

    def test_viewer_token_returns_403(self, client, auth):
        response = client.patch(
            "/api/v1/sensors/SENSOR-001/status",
            json={"is_active": False},
            headers=auth("operario@demo.com"),
        )

        assert response.status_code == 403
        assert "permisos de Administrador" in response.json()["detail"]

    def test_admin_can_activate_sensor(
        self, client, monkeypatch, db, auth
    ):
        telegram_send = self._mock_telegram(monkeypatch)

        sensor = db.get(Sensor, "SENSOR-001")
        sensor.is_active = False
        db.commit()

        response = client.patch(
            "/api/v1/sensors/SENSOR-001/status",
            json={"is_active": True},
            headers=auth("admin@demo.com"),
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True
        telegram_send.assert_awaited_once()

    def test_update_deactivates_sensor(
        self, client, monkeypatch, auth
    ):
        self._mock_telegram(monkeypatch)

        response = client.patch(
            "/api/v1/sensors/SENSOR-001/status",
            json={"is_active": False},
            headers=auth("admin@demo.com"),
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_no_change_does_not_notify(
        self, client, monkeypatch, auth
    ):
        telegram_send = self._mock_telegram(monkeypatch)

        response = client.patch(
            "/api/v1/sensors/SENSOR-001/status",
            json={"is_active": True},
            headers=auth("admin@demo.com"),
        )

        assert response.status_code == 200
        assert response.json()["is_active"] is True
        telegram_send.assert_not_called()

    def test_unknown_sensor_returns_404(
        self, client, monkeypatch, auth
    ):
        self._mock_telegram(monkeypatch)

        response = client.patch(
            "/api/v1/sensors/NO-EXISTE/status",
            json={"is_active": False},
            headers=auth("admin@demo.com"),
        )

        assert response.status_code == 404

    def test_invalid_payload_returns_422(self, client, auth):
        response = client.patch(
            "/api/v1/sensors/SENSOR-001/status",
            json={},
            headers=auth("admin@demo.com"),
        )

        assert response.status_code == 422
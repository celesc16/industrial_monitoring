"""Tests of the maintenance scheduling endpoint."""

from datetime import datetime, timedelta, timezone

from app.models.reading import Reading

SCHEDULE_URL = "/api/v1/maintenance/sensors/SENSOR-001/schedule"

EXPECTED_KEYS = {
    "sensor_id",
    "recommended_window_days",
    "minimum_window_days",
    "maximum_window_days",
    "expected_cost_per_day",
    "expected_unplanned_cost_per_day",
    "expected_planned_cost_per_day",
    "failure_probability_at_window",
    "weibull_shape",
    "weibull_scale_days",
    "parameters_estimated",
    "run_to_failure_cost_per_day",
    "avoided_cost_per_day",
    "config_used",
}


def _add_anomaly_history(db, sensor_id="SENSOR-001", count=9) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add_all([
        Reading(
            timestamp=now - timedelta(hours=hour),
            sensor_id=sensor_id,
            temperature=60.0 + hour,
            vibration=1.5,
            pressure=100.0,
            prediction=-1 if hour % 2 == 0 else 1,
            is_anomaly=hour % 2 == 0,
            anomaly_score=-0.5 if hour % 2 == 0 else 0.4,
        )
        for hour in range(count)
    ])
    db.commit()


class TestComputeMaintenanceSchedule:
    def test_returns_schedule_with_default_config(self, client):
        response = client.post(SCHEDULE_URL)

        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) == EXPECTED_KEYS
        assert body["sensor_id"] == "SENSOR-001"
        assert body["recommended_window_days"] > 0
        assert body["parameters_estimated"] is False

    def test_custom_body_config_is_echoed(self, client):
        response = client.post(
            SCHEDULE_URL,
            json={
                "preventive_cost": 5_000.0,
                "failure_cost": 50_000.0,
            },
        )

        assert response.status_code == 200
        config = response.json()["config_used"]
        assert config["preventive_cost"] == 5_000.0
        assert config["failure_cost"] == 50_000.0
        assert config["min_window_days"] > 0

    def test_anomaly_history_enables_estimation(self, client, db):
        _add_anomaly_history(db)

        body = client.post(SCHEDULE_URL).json()

        assert body["parameters_estimated"] is True
        assert body["weibull_shape"] > 0
        assert body["weibull_scale_days"] > 0
        assert (
            body["minimum_window_days"]
            <= body["recommended_window_days"]
            <= body["maximum_window_days"]
        )

    def test_invalid_config_returns_422(self, client):
        response = client.post(
            SCHEDULE_URL,
            json={
                "preventive_cost": 10_000.0,
                "failure_cost": 1_000.0,
            },
        )

        assert response.status_code == 422

    def test_unknown_sensor_returns_404(self, client):
        response = client.post(
            "/api/v1/maintenance/sensors/NO-EXISTE/schedule"
        )

        assert response.status_code == 404
        assert "no está registrado" in response.json()["detail"]

    def test_endpoint_is_public(self, client):
        response = client.post(SCHEDULE_URL)

        assert response.status_code == 200
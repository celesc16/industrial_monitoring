import pytest

from app.services import alert_policy
from app.services.alert_policy import (
    REQUIRED_CONSECUTIVE_ANOMALIES,
    reset_sensor_alert,
    should_notify_anomaly,
)


@pytest.fixture(autouse=True)
def clean_alert_states():
    """Vacía el estado global entre tests (evita contaminación)."""
    reset_sensor_alert("any-sensor")
    yield
    alert_policy._sensor_states.clear()


def test_normal_lecture_never_triggers_notification():
    assert should_notify_anomaly("SENSOR-001", is_anomaly=False) is False
    assert should_notify_anomaly("SENSOR-001", is_anomaly=False) is False


def test_first_anomalies_do_not_notify_until_threshold():
    sensor_id = "SENSOR-001"

    for _ in range(REQUIRED_CONSECUTIVE_ANOMALIES - 1):
        assert should_notify_anomaly(sensor_id, is_anomaly=True) is False


def test_hitting_threshold_notifies_once():
    sensor_id = "SENSOR-001"
    results = [
        should_notify_anomaly(sensor_id, is_anomaly=True)
        for _ in range(REQUIRED_CONSECUTIVE_ANOMALIES)
    ]

    assert results == [False] * (REQUIRED_CONSECUTIVE_ANOMALIES - 1) + [True]


def test_does_not_notify_again_for_same_anomaly_episode():
    sensor_id = "SENSOR-001"

    for _ in range(REQUIRED_CONSECUTIVE_ANOMALIES):
        should_notify_anomaly(sensor_id, is_anomaly=True)

    assert should_notify_anomaly(sensor_id, is_anomaly=True) is False


def test_normal_lecture_resets_anomaly_counter():
    sensor_id = "SENSOR-001"

    for _ in range(REQUIRED_CONSECUTIVE_ANOMALIES - 1):
        should_notify_anomaly(sensor_id, is_anomaly=True)

    should_notify_anomaly(sensor_id, is_anomaly=False)

    assert should_notify_anomaly(sensor_id, is_anomaly=True) is False
    assert should_notify_anomaly(sensor_id, is_anomaly=True) is False
    assert should_notify_anomaly(sensor_id, is_anomaly=True) is True


def test_reset_sensor_alert_clears_state():
    sensor_id = "SENSOR-001"

    for _ in range(REQUIRED_CONSECUTIVE_ANOMALIES):
        should_notify_anomaly(sensor_id, is_anomaly=True)

    reset_sensor_alert(sensor_id)

    assert should_notify_anomaly(sensor_id, is_anomaly=True) is False


def test_states_are_isolated_per_sensor():
    for _ in range(REQUIRED_CONSECUTIVE_ANOMALIES - 1):
        should_notify_anomaly("SENSOR-001", is_anomaly=True)
        should_notify_anomaly("SENSOR-002", is_anomaly=True)

    assert should_notify_anomaly("SENSOR-001", is_anomaly=True) is True
    assert should_notify_anomaly("SENSOR-002", is_anomaly=True) is True
    assert should_notify_anomaly("SENSOR-003", is_anomaly=True) is False
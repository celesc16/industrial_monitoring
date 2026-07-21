from dataclasses import dataclass
from threading import Lock


REQUIRED_CONSECUTIVE_ANOMALIES = 3


@dataclass
class SensorAlertState:
    consecutive_anomalies: int = 0
    notification_sent: bool = False


_sensor_states: dict[str, SensorAlertState] = {}
_state_lock = Lock()


def should_notify_anomaly(
    sensor_id: str,
    is_anomaly: bool,
) -> bool:
    """
    Decide si corresponde enviar una notificación.

    No clasifica la lectura. La clasificación ya fue realizada
    previamente por el modelo de Machine Learning.
    """
    with _state_lock:
        state = _sensor_states.setdefault(
            sensor_id,
            SensorAlertState(),
        )

        if not is_anomaly:
            state.consecutive_anomalies = 0
            state.notification_sent = False
            return False

        state.consecutive_anomalies += 1

        if state.consecutive_anomalies < REQUIRED_CONSECUTIVE_ANOMALIES:
            return False

        if state.notification_sent:
            return False

        state.notification_sent = True
        return True


def reset_sensor_alert(sensor_id: str) -> None:
    """
    Reinicia el estado de alertas de un sensor.

    Es útil cuando el sensor se activa o desactiva manualmente.
    """
    with _state_lock:
        _sensor_states.pop(sensor_id, None)
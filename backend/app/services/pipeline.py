import logging
from datetime import datetime

from app.core.exceptions import InactiveSensorError, SensorNotFoundError
from app.db.session import SessionLocal
from app.models.reading import Reading
from app.models.sensor import Sensor
from app.schemas.reading import SensorReadingIn
from app.services.ml_model import AnomalyDetector
from app.services.telegram_bot import build_alert_message, send_telegram_alert
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


async def process_reading(
    payload: dict,
    detector: AnomalyDetector,
) -> dict:
    
    data = SensorReadingIn(**payload)

    result = detector.predict(
        {
            "temperature": data.temperature,
            "vibration": data.vibration,
            "pressure": data.pressure,
        }
    )

    db = SessionLocal()

    try:
        sensor = db.get(Sensor, data.sensor_id)

        if sensor is None:
            raise SensorNotFoundError(data.sensor_id)

        if not sensor.is_active:
            raise InactiveSensorError(data.sensor_id)

        current_time = datetime.utcnow()

        reading = Reading(
            timestamp=current_time,
            sensor_id=sensor.id,
            temperature=data.temperature,
            vibration=data.vibration,
            pressure=data.pressure,
            prediction=result["prediction"],
            is_anomaly=result["is_anomaly"],
            anomaly_score=result["anomaly_score"],
        )

        sensor.last_seen_at = current_time

        db.add(reading)
        db.commit()
        db.refresh(reading)

        record = {
            "id": reading.id,
            "timestamp": reading.timestamp.isoformat(),
            "sensor_id": sensor.id,
            "temperature": reading.temperature,
            "vibration": reading.vibration,
            "pressure": reading.pressure,
            "prediction": reading.prediction,
            "is_anomaly": reading.is_anomaly,
            "anomaly_score": reading.anomaly_score,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    await manager.broadcast(record)

    if result["is_anomaly"]:
        logger.warning("Anomalía detectada: %s", record)

        message = build_alert_message(
            sensor_id=data.sensor_id,
            temperature=data.temperature,
            vibration=data.vibration,
            pressure=data.pressure,
            score=result["anomaly_score"],
        )

        await send_telegram_alert(message)

    return record
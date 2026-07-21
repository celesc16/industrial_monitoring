import logging
from datetime import datetime

from app.core.exceptions import (
    InactiveSensorError,
    SensorNotFoundError,
)
from app.db.session import SessionLocal
from app.models.reading import Reading
from app.models.sensor import Sensor
from app.schemas.reading import SensorReadingIn
from app.services.ml_model import AnomalyDetector
from app.services.telegram_bot import (
    build_alert_message,
    send_telegram_alert,
)
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


async def process_reading(
    payload: dict,
    detector: AnomalyDetector,
) -> dict:
    """
    Valida, analiza y procesa una lectura.

    La clasificación normal/anómala es realizada exclusivamente
    por el modelo de Machine Learning.
    """
    data = SensorReadingIn(**payload)

    db = SessionLocal()

    try:
        sensor = db.get(Sensor, data.sensor_id)

        if sensor is None:
            raise SensorNotFoundError(data.sensor_id)

        if not sensor.is_active:
            raise InactiveSensorError(data.sensor_id)

        # La IA determina si la lectura es normal o anómala.
        result = detector.predict(
            {
                "temperature": data.temperature,
                "vibration": data.vibration,
                "pressure": data.pressure,
            }
        )

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
            "sensor_id": reading.sensor_id,
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

    if record["is_anomaly"]:
        logger.warning(
            "La IA detectó una lectura anómala | "
            "sensor=%s | temp=%.2f | vib=%.2f | "
            "presión=%.2f | score=%.5f",
            record["sensor_id"],
            record["temperature"],
            record["vibration"],
            record["pressure"],
            record["anomaly_score"],
        )

        message = build_alert_message(
            sensor_id=record["sensor_id"],
            temperature=record["temperature"],
            vibration=record["vibration"],
            pressure=record["pressure"],
            score=record["anomaly_score"],
        )

        sent = await send_telegram_alert(message)

        if sent:
            logger.info(
                "Alerta enviada a Telegram | sensor=%s | lectura=%s",
                record["sensor_id"],
                record["id"],
            )

    else:
        logger.info(
            "La IA clasificó la lectura como normal | "
            "sensor=%s | score=%.5f",
            record["sensor_id"],
            record["anomaly_score"],
        )

    return record
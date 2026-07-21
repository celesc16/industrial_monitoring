import logging
from datetime import datetime

from app.db.session import SessionLocal
from app.models.reading import Reading
from app.schemas.reading import SensorReadingIn
from app.services.ml_model import AnomalyDetector
from app.services.telegram_bot import build_alert_message, send_telegram_alert
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


async def process_reading(payload: dict, detector: AnomalyDetector) -> dict:
    """
    Evalúa una lectura con IA, la persiste, la difunde por WebSocket y
    dispara la alerta de Telegram si corresponde. Es el punto de entrada
    único usado tanto por el cliente MQTT como por el endpoint de prueba.
    """
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
        reading = Reading(
            timestamp=datetime.utcnow(),
            sensor_id=data.sensor_id,
            temperature=data.temperature,
            vibration=data.vibration,
            pressure=data.pressure,
            prediction=result["prediction"],
            is_anomaly=result["is_anomaly"],
            anomaly_score=result["anomaly_score"],
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)
    finally:
        db.close()

    record = {
        "id": reading.id,
        "timestamp": reading.timestamp.isoformat(),
        "sensor_id": data.sensor_id,
        "temperature": data.temperature,
        "vibration": data.vibration,
        "pressure": data.pressure,
        "prediction": result["prediction"],
        "is_anomaly": result["is_anomaly"],
        "anomaly_score": result["anomaly_score"],
    }

    await manager.broadcast(record)

    if result["is_anomaly"]:
        logger.warning("Anomalía detectada: %s", record)
        mensaje = build_alert_message(
            data.sensor_id, data.temperature, data.vibration, data.pressure, result["anomaly_score"]
        )
        await send_telegram_alert(mensaje)

    return record

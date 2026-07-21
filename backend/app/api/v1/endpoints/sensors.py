import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.sensor import Sensor
from app.schemas.sensor import SensorOut, SensorStatusUpdate
from app.services.sensor_service import serialize_sensor
from app.services.telegram_bot import (
    build_sensor_status_message,
    send_telegram_alert,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sensors"])


@router.get(
    "/sensors",
    response_model=list[SensorOut],
)
def get_sensors(
    db: Session = Depends(get_db),
):
    sensors = (
        db.query(Sensor)
        .order_by(Sensor.id.asc())
        .all()
    )

    return [
        serialize_sensor(db, sensor)
        for sensor in sensors
    ]


@router.get(
    "/sensors/{sensor_id}",
    response_model=SensorOut,
)
def get_sensor(
    sensor_id: str,
    db: Session = Depends(get_db),
):
    sensor = db.get(Sensor, sensor_id)

    if sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El sensor '{sensor_id}' no está registrado.",
        )

    return serialize_sensor(db, sensor)


@router.patch(
    "/sensors/{sensor_id}/status",
    response_model=SensorOut,
)
async def update_sensor_status(
    sensor_id: str,
    payload: SensorStatusUpdate,
    db: Session = Depends(get_db),
):
    if not settings.demo_controls_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los controles de demostración están deshabilitados.",
        )

    sensor = db.get(Sensor, sensor_id)

    if sensor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El sensor '{sensor_id}' no está registrado.",
        )

    previous_status = sensor.is_active

    # Evita guardar y notificar cuando el estado no cambió.
    if previous_status == payload.is_active:
        logger.info(
            "El sensor %s ya se encontraba %s.",
            sensor.id,
            "activo" if sensor.is_active else "inactivo",
        )

        return serialize_sensor(db, sensor)

    sensor.is_active = payload.is_active

    try:
        db.commit()
        db.refresh(sensor)

    except Exception:
        db.rollback()
        logger.exception(
            "Error actualizando el estado del sensor %s.",
            sensor_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo actualizar el estado del sensor.",
        )

    logger.info(
        "Sensor %s %s mediante controles de demostración.",
        sensor.id,
        "activado" if sensor.is_active else "desactivado",
    )

    message = build_sensor_status_message(
        sensor_id=sensor.id,
        sensor_name=sensor.name,
        is_active=sensor.is_active,
    )

    telegram_sent = await send_telegram_alert(message)

    if telegram_sent:
        logger.info(
            "Notificación de cambio de estado enviada a Telegram | "
            "sensor=%s | estado=%s",
            sensor.id,
            "activo" if sensor.is_active else "inactivo",
        )
    else:
        logger.warning(
            "El estado del sensor %s fue actualizado, pero no se pudo "
            "enviar la notificación a Telegram.",
            sensor.id,
        )

    return serialize_sensor(db, sensor)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.sensor import Sensor
from app.schemas.sensor import SensorOut
from app.services.sensor_service import serialize_sensor

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
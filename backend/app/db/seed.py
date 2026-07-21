import logging

from sqlalchemy.orm import Session

from app.models.sensor import Sensor

logger = logging.getLogger(__name__)


INITIAL_SENSORS = [
    {
        "id": "SENSOR-001",
        "name": "Motor principal",
        "location": "Línea de producción A",
        "description": "Monitoreo del motor principal de la planta.",
    },
    {
        "id": "SENSOR-002",
        "name": "Compresor",
        "location": "Sala de compresores",
        "description": "Monitoreo del sistema principal de compresión.",
    },
    {
        "id": "SENSOR-003",
        "name": "Bomba hidráulica",
        "location": "Sector hidráulico",
        "description": "Monitoreo de la bomba hidráulica de producción.",
    },
    {
        "id": "SENSOR-004",
        "name": "Cinta transportadora",
        "location": "Línea de producción B",
        "description": "Monitoreo del sistema de transporte de materiales.",
    },
    {
        "id": "SENSOR-005",
        "name": "Generador",
        "location": "Sala eléctrica",
        "description": "Monitoreo del generador eléctrico auxiliar.",
    },
]


def seed_sensors(db: Session) -> None:
    existing_ids = {
        sensor_id
        for (sensor_id,) in db.query(Sensor.id).all()
    }

    sensors_to_create = [
        Sensor(**sensor_data)
        for sensor_data in INITIAL_SENSORS
        if sensor_data["id"] not in existing_ids
    ]

    if not sensors_to_create:
        logger.info("Los sensores iniciales ya se encuentran registrados.")
        return

    db.add_all(sensors_to_create)
    db.commit()

    logger.info(
        "Se registraron %d sensores iniciales.",
        len(sensors_to_create),
    )
import logging

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.sensor import Sensor
from app.models.user import Role, User

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


# Cuentas demo para que un evaluador pueda probar la plataforma sin
# registrarse. La misma contraseña se usa para los dos roles.
DEMO_USERS = [
    {
        "email": "admin@demo.com",
        "password": "1234",
        "role": Role.ADMIN,
    },
    {
        "email": "operario@demo.com",
        "password": "1234",
        "role": Role.VIEWER,
    },
]


def seed_users(db: Session) -> None:
    users_to_create = []

    for user_data in DEMO_USERS:
        user = (
            db.query(User)
            .filter(User.email == user_data["email"])
            .first()
        )

        if user is not None:
            continue

        users_to_create.append(
            User(
                email=user_data["email"],
                hashed_password=hash_password(
                    user_data["password"]
                ),
                role=user_data["role"],
            )
        )

    if not users_to_create:
        logger.info("Los usuarios demo ya se encuentran registrados.")
        return

    db.add_all(users_to_create)
    db.commit()

    logger.info(
        "Se registraron %d usuarios demo.",
        len(users_to_create),
    )
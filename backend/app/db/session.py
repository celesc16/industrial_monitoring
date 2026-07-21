from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db() -> None:
    from app.db.base import Base

    from app.models import Reading, Sensor  # noqa: F401
    from app.db.seed import seed_sensors

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        seed_sensors(db)
    finally:
        db.close()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    sensor_id = Column(
        String(50),
        ForeignKey("sensors.id"),
        nullable=False,
        index=True,
    )

    temperature = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)

    prediction = Column(Integer, nullable=False)
    is_anomaly = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
    anomaly_score = Column(Float, nullable=False)

    sensor = relationship(
        "Sensor",
        back_populates="readings",
    )
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String(50), primary_key=True, index=True)

    name = Column(String(120), nullable=False)
    location = Column(String(180), nullable=False)
    description = Column(String(255), nullable=True)

    is_active = Column(Boolean, nullable=False, default=True, index=True)

    last_seen_at = Column(DateTime, nullable=True, index=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    readings = relationship(
        "Reading",
        back_populates="sensor",
    )
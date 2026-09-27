import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String

from app.db.base import Base


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    VIEWER = "VIEWER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password = Column(String(255), nullable=False)

    role = Column(
        Enum(Role),
        nullable=False,
        default=Role.VIEWER,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
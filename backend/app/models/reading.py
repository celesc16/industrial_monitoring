from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.db.base import Base


class Reading(Base):

    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sensor_id = Column(String, index=True)

    temperature = Column(Float)
    vibration = Column(Float)
    pressure = Column(Float)

    prediction = Column(Integer)  
    is_anomaly = Column(Boolean, default=False, index=True)
    anomaly_score = Column(Float) 

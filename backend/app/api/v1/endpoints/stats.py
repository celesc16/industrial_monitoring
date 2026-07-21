from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reading import Reading
from app.schemas.reading import StatsOut

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Reading.id)).scalar() or 0
    total_anomalies = db.query(func.count(Reading.id)).filter(Reading.is_anomaly == True).scalar() or 0  # noqa: E712

    last_24h = datetime.utcnow() - timedelta(hours=24)
    anomalies_24h = (
        db.query(func.count(Reading.id))
        .filter(Reading.is_anomaly == True, Reading.timestamp >= last_24h)  # noqa: E712
        .scalar()
        or 0
    )

    latest = db.query(Reading).order_by(Reading.timestamp.desc()).first()

    return StatsOut(
        total_readings=total,
        total_anomalies=total_anomalies,
        anomalies_last_24h=anomalies_24h,
        latest_reading=latest,
    )

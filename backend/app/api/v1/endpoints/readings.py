from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reading import Reading
from app.schemas.reading import ReadingOut

router = APIRouter(tags=["readings"])


@router.get("/readings", response_model=list[ReadingOut])
def get_readings(limit: int = 100, only_anomalies: bool = False, db: Session = Depends(get_db)):
    query = db.query(Reading)
    if only_anomalies:
        query = query.filter(Reading.is_anomaly == True)  # noqa: E712
    rows = query.order_by(Reading.timestamp.desc()).limit(limit).all()
    return list(reversed(rows))  

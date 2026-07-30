from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reading import Reading
from app.schemas.reading import StatsOut

router = APIRouter(tags=["stats"])


def utc_now_naive() -> datetime:
    """
    Devuelve la fecha UTC sin zona horaria.

    Se mantiene como fecha naive porque actualmente
    Reading.timestamp se guarda de esa manera.
    """
    return datetime.now(timezone.utc).replace(
        tzinfo=None
    )


@router.get(
    "/stats",
    response_model=StatsOut,
)
def get_stats(
    sensor_id: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
    ),
    db: Session = Depends(get_db),
):
    common_filters = []

    if sensor_id:
        common_filters.append(
            Reading.sensor_id == sensor_id
        )

    total_readings = (
        db.query(func.count(Reading.id))
        .filter(*common_filters)
        .scalar()
        or 0
    )

    total_anomalies = (
        db.query(func.count(Reading.id))
        .filter(
            *common_filters,
            Reading.is_anomaly.is_(True),
        )
        .scalar()
        or 0
    )

    last_24h = (
        utc_now_naive()
        - timedelta(hours=24)
    )

    anomalies_last_24h = (
        db.query(func.count(Reading.id))
        .filter(
            *common_filters,
            Reading.is_anomaly.is_(True),
            Reading.timestamp >= last_24h,
        )
        .scalar()
        or 0
    )

    latest_reading = (
        db.query(Reading)
        .filter(*common_filters)
        .order_by(
            Reading.timestamp.desc(),
            Reading.id.desc(),
        )
        .first()
    )

    return StatsOut(
        total_readings=total_readings,
        total_anomalies=total_anomalies,
        anomalies_last_24h=(
            anomalies_last_24h
        ),
        latest_reading=latest_reading,
    )
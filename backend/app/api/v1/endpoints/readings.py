import math
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.reading import Reading
from app.schemas.reading import ReadingsPageOut

router = APIRouter(tags=["readings"])


@router.get(
    "/readings",
    response_model=ReadingsPageOut,
)
def get_readings(
    page: int = Query(
        default=1,
        ge=1,
        description="Número de página",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Cantidad de lecturas por página",
    ),
    sensor_id: str | None = Query(
        default=None,
        description="Identificador del sensor",
    ),
    is_anomaly: bool | None = Query(
        default=None,
        description="Filtrar por lecturas normales o anómalas",
    ),
    date_from: datetime | None = Query(
        default=None,
        description="Fecha y hora inicial",
    ),
    date_to: datetime | None = Query(
        default=None,
        description="Fecha y hora final",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Reading)

    if sensor_id:
        query = query.filter(
            Reading.sensor_id == sensor_id
        )

    if is_anomaly is not None:
        query = query.filter(
            Reading.is_anomaly == is_anomaly
        )

    if date_from is not None:
        query = query.filter(
            Reading.timestamp >= date_from
        )

    if date_to is not None:
        query = query.filter(
            Reading.timestamp <= date_to
        )

    total_items = query.count()

    total_pages = (
        math.ceil(total_items / page_size)
        if total_items > 0
        else 0
    )

    offset = (page - 1) * page_size

    readings = (
        query
        .order_by(
            Reading.timestamp.desc(),
            Reading.id.desc(),
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "items": readings,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }
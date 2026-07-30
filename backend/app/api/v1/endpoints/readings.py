from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.reading import ReadingsPageOut
from app.services.reading_service import (
    create_readings_csv_filename,
    generate_readings_csv,
    get_readings_for_export,
    get_readings_page,
)


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
        description=(
            "Filtrar por lecturas normales "
            "o anómalas"
        ),
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
    readings, pagination = (
        get_readings_page(
            db=db,
            page=page,
            page_size=page_size,
            sensor_id=sensor_id,
            is_anomaly=is_anomaly,
            date_from=date_from,
            date_to=date_to,
        )
    )

    return {
        "items": readings,
        "pagination": pagination,
    }


@router.get(
    "/readings/export",
    summary="Exportar lecturas en formato CSV",
)
def export_readings_csv(
    sensor_id: str | None = Query(
        default=None,
        description="Identificador del sensor",
    ),
    is_anomaly: bool | None = Query(
        default=None,
        description=(
            "Filtrar por lecturas normales "
            "o anómalas"
        ),
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
    readings = get_readings_for_export(
        db=db,
        sensor_id=sensor_id,
        is_anomaly=is_anomaly,
        date_from=date_from,
        date_to=date_to,
    )

    filename = (
        create_readings_csv_filename()
    )

    return StreamingResponse(
        generate_readings_csv(readings),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
        },
    )
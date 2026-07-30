import csv
import io
import math
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.reading import Reading


LOCAL_TIME_ZONE = ZoneInfo(
    settings.app_time_zone
)

DB_BATCH_SIZE = settings.readings_db_batch_size
CSV_BATCH_SIZE = settings.readings_csv_batch_size


def normalize_filter_datetime(
    value: datetime | None,
) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None:
        return value

    return (
        value
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )


def to_local_datetime(
    value: datetime,
) -> datetime:
    if value.tzinfo is None:
        value = value.replace(
            tzinfo=timezone.utc
        )

    return value.astimezone(
        LOCAL_TIME_ZONE
    )


def apply_reading_filters(
    query,
    sensor_id: str | None = None,
    is_anomaly: bool | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    date_from = normalize_filter_datetime(
        date_from
    )

    date_to = normalize_filter_datetime(
        date_to
    )

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

    return query


def get_readings_page(
    db: Session,
    page: int,
    page_size: int,
    sensor_id: str | None = None,
    is_anomaly: bool | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    query = apply_reading_filters(
        query=db.query(Reading),
        sensor_id=sensor_id,
        is_anomaly=is_anomaly,
        date_from=date_from,
        date_to=date_to,
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

    pagination = {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
    }

    return readings, pagination


def get_readings_for_export(
    db: Session,
    sensor_id: str | None = None,
    is_anomaly: bool | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    query = apply_reading_filters(
        query=db.query(Reading),
        sensor_id=sensor_id,
        is_anomaly=is_anomaly,
        date_from=date_from,
        date_to=date_to,
    )

    return (
        query
        .order_by(
            Reading.timestamp.desc(),
            Reading.id.desc(),
        )
        .yield_per(DB_BATCH_SIZE)
    )


def format_decimal(
    value: float,
    decimals: int,
) -> str:
    return (
        f"{value:.{decimals}f}"
        .replace(".", ",")
    )


def generate_readings_csv(
    readings: Iterable[Reading],
) -> Iterator[str]:
    buffer = io.StringIO(newline="")

    buffer.write("\ufeff")

    writer = csv.writer(
        buffer,
        delimiter=";",
        lineterminator="\n",
    )

    writer.writerow([
        "Fecha",
        "Hora",
        "Sensor",
        "Temperatura (°C)",
        "Vibración (mm/s)",
        "Presión (kPa)",
        "Estado",
        "Score",
    ])

    for row_number, reading in enumerate(
        readings,
        start=1,
    ):
        local_timestamp = to_local_datetime(
            reading.timestamp
        )

        formatted_time = (
            local_timestamp.strftime(
                "%H:%M:%S"
            )
        )

        writer.writerow([
            local_timestamp.strftime(
                "%d/%m/%Y"
            ),
            f'="{formatted_time}"',
            reading.sensor_id,
            format_decimal(
                reading.temperature,
                2,
            ),
            format_decimal(
                reading.vibration,
                2,
            ),
            format_decimal(
                reading.pressure,
                2,
            ),
            (
                "Anomalía"
                if reading.is_anomaly
                else "Normal"
            ),
            format_decimal(
                reading.anomaly_score,
                4,
            ),
        ])

        if row_number % CSV_BATCH_SIZE == 0:
            yield buffer.getvalue()

            buffer.seek(0)
            buffer.truncate(0)

    remaining_content = buffer.getvalue()

    if remaining_content:
        yield remaining_content


def create_readings_csv_filename() -> str:
    local_now = datetime.now(
        LOCAL_TIME_ZONE
    )

    return (
        "lecturas_industriales_"
        f"{local_now.strftime('%Y%m%d_%H%M%S')}"
        ".csv"
    )
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.models.reading import Reading
from app.services.reading_service import (
    apply_reading_filters,
    create_readings_csv_filename,
    format_decimal,
    generate_readings_csv,
    get_readings_for_export,
    get_readings_page,
    normalize_filter_datetime,
    to_local_datetime,
)

LOCAL_TZ = ZoneInfo("America/Argentina/Mendoza")


def _make_reading(
    *,
    timestamp: datetime,
    sensor_id: str = "SENSOR-001",
    temperature: float = 60.0,
    vibration: float = 1.5,
    pressure: float = 100.0,
    is_anomaly: bool = False,
    anomaly_score: float = 0.2,
) -> Reading:
    return Reading(
        timestamp=timestamp,
        sensor_id=sensor_id,
        temperature=temperature,
        vibration=vibration,
        pressure=pressure,
        prediction=-1 if is_anomaly else 1,
        is_anomaly=is_anomaly,
        anomaly_score=anomaly_score,
    )


class TestNormalizeFilterDatetime:
    def test_none_stays_none(self):
        assert normalize_filter_datetime(None) is None

    def test_naive_datetime_is_kept(self):
        naive = datetime(2026, 1, 1, 12, 0, 0)

        assert normalize_filter_datetime(naive) == naive

    def test_aware_utc_is_flattened_to_naive(self):
        aware = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = normalize_filter_datetime(aware)

        assert result == datetime(2026, 1, 1, 12, 0, 0)
        assert result.tzinfo is None

    def test_aware_other_zone_is_converted_to_utc(self):
        aware = datetime(
            2026, 1, 1, 9, 0, 0,
            tzinfo=ZoneInfo("America/Argentina/Mendoza"),
        )
        result = normalize_filter_datetime(aware)

        assert result == datetime(2026, 1, 1, 12, 0, 0)
        assert result.tzinfo is None


class TestToLocalDatetime:
    def test_naive_is_interpreted_as_utc_and_converted(self):
        naive = datetime(2026, 1, 1, 12, 0, 0)
        result = to_local_datetime(naive)

        assert result == naive.replace(tzinfo=timezone.utc).astimezone(LOCAL_TZ)

    def test_aware_utc_is_converted(self):
        aware = datetime(2026, 1, 1, 15, 0, 0, tzinfo=timezone.utc)
        result = to_local_datetime(aware)

        assert result.tzinfo == LOCAL_TZ
        assert result.hour == 12  # UTC-3


class TestFormatDecimal:
    def test_formats_with_comma_decimal_separator(self):
        assert format_decimal(3.14159, 2) == "3,14"
        assert format_decimal(-1.5, 1) == "-1,5"


class TestGenerateReadingsCsv:
    def test_emits_header_and_row(self):
        reading = _make_reading(
            timestamp=datetime(2026, 1, 15, 14, 30, 45),
            sensor_id="SENSOR-001",
            temperature=60.1234,
            vibration=1.5678,
            pressure=100.9876,
            is_anomaly=True,
            anomaly_score=-0.54321,
        )

        content = "".join(generate_readings_csv([reading]))

        assert "Sensor;Temperatura" in content
        assert "SENSOR-001" in content
        assert "Anomalía" in content
        assert "-0,5432" in content

    def test_empty_readings_only_header(self):
        content = "".join(generate_readings_csv([]))

        assert content.startswith("\ufeff")
        assert "Fecha" in content

    def test_filename_matches_expected_pattern(self):
        name = create_readings_csv_filename()

        assert re.fullmatch(
            r"lecturas_industriales_\d{8}_\d{6}\.csv",
            name,
        )


def _seed_three_readings(db) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add_all([
        _make_reading(
            timestamp=now,
            sensor_id="SENSOR-001",
            temperature=60.0,
            is_anomaly=False,
        ),
        _make_reading(
            timestamp=now - timedelta(minutes=1),
            sensor_id="SENSOR-001",
            temperature=92.0,
            is_anomaly=True,
            anomaly_score=-0.4,
        ),
        _make_reading(
            timestamp=now - timedelta(minutes=2),
            sensor_id="SENSOR-002",
            temperature=55.0,
            is_anomaly=False,
        ),
    ])
    db.commit()


class TestGetReadingsPage:
    def test_empty_db_returns_empty_page(self, db):
        readings, pagination = get_readings_page(db, page=1, page_size=20)

        assert readings == []
        assert pagination["total_items"] == 0
        assert pagination["total_pages"] == 0
        assert pagination["page"] == 1
        assert pagination["page_size"] == 20

    def test_returns_all_readings_sorted_newest_first(self, db):
        _seed_three_readings(db)

        readings, pagination = get_readings_page(db, page=1, page_size=20)

        assert pagination["total_items"] == 3
        assert pagination["total_pages"] == 1
        assert [r.sensor_id for r in readings] == [
            "SENSOR-001",
            "SENSOR-001",
            "SENSOR-002",
        ]

    def test_pagination_splits_in_pages(self, db):
        _seed_three_readings(db)

        _, pagination = get_readings_page(db, page=1, page_size=2)
        assert pagination["total_pages"] == 2

        page_two, _ = get_readings_page(db, page=2, page_size=2)
        assert len(page_two) == 1

    def test_filters_by_sensor(self, db):
        _seed_three_readings(db)

        readings, pagination = get_readings_page(
            db, page=1, page_size=20, sensor_id="SENSOR-002"
        )

        assert pagination["total_items"] == 1
        assert readings[0].sensor_id == "SENSOR-002"

    def test_filters_by_anomaly(self, db):
        _seed_three_readings(db)

        readings, pagination = get_readings_page(
            db, page=1, page_size=20, is_anomaly=True
        )

        assert pagination["total_items"] == 1
        assert readings[0].is_anomaly is True

    def test_filters_by_date_range(self, db):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        db.add_all([
            _make_reading(timestamp=now - timedelta(hours=3)),
            _make_reading(timestamp=now - timedelta(hours=1)),
        ])
        db.commit()

        readings, pagination = get_readings_page(
            db,
            page=1,
            page_size=20,
            date_from=now - timedelta(hours=2),
        )

        assert pagination["total_items"] == 1


class TestGetReadingsForExport:
    def test_respects_filters(self, db):
        _seed_three_readings(db)

        readings = list(
            get_readings_for_export(db, sensor_id="SENSOR-001")
        )

        assert len(readings) == 2
        assert all(r.sensor_id == "SENSOR-001" for r in readings)


class TestApplyReadingFilters:
    def test_returns_query_unchanged_without_filters(self, db):
        query = apply_reading_filters(db.query(Reading))

        assert query.count() == 0
from datetime import date, datetime

from ariadne import ScalarType

# === Scalar Date ===
date_scalar = ScalarType("Date")


@date_scalar.serializer
def serialize_date(value: date) -> str | None:
    return value.isoformat() if value else None


@date_scalar.value_parser
def parse_date_value(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


# === Scalar DateTime ===
datetime_scalar = ScalarType("DateTime")


@datetime_scalar.serializer
def serialize_datetime(value: datetime) -> str | None:
    return value.isoformat() if value else None


@datetime_scalar.value_parser
def parse_datetime_value(value: str) -> datetime | None:
    return datetime.fromisoformat(value) if value else None

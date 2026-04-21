from datetime import UTC, datetime, timedelta


def get_utc_now():
    return datetime.now(UTC).replace(tzinfo=None)


def get_utc_with_delta(**kwargs):
    return datetime.now(UTC) + timedelta(**kwargs)

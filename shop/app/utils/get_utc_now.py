from datetime import datetime, timezone, timedelta


def get_utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_utc_with_delta(**kwargs):
    return datetime.now(timezone.utc) + timedelta(**kwargs)

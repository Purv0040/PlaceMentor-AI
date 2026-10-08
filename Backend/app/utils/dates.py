import zoneinfo
from datetime import datetime, timezone, timedelta

APP_TIMEZONE = zoneinfo.ZoneInfo("Asia/Kolkata")


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def local_now(tz=APP_TIMEZONE) -> datetime:
    """Return current timezone-aware local datetime."""
    return datetime.now(tz)


def get_today_date_str(tz=APP_TIMEZONE) -> str:
    """Return today's date formatted as YYYY-MM-DD in the application local timezone."""
    return datetime.now(tz).strftime("%Y-%m-%d")


def format_iso(dt: datetime) -> str:
    """Return ISO formatted datetime string."""
    return dt.isoformat()


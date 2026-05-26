from __future__ import annotations

from datetime import datetime, timezone
from dateutil import tz as dateutil_tz

_DALLAS_TZ = dateutil_tz.gettz('America/Chicago')


def ensure_utc(dt: datetime | None) -> datetime | None:
    """Return dt converted to UTC.

    Naive input is assumed to be America/Chicago (Dallas local time) and
    localized before converting to UTC — DST (CDT/CST) is handled
    automatically via the IANA 'America/Chicago' identifier.
    Tz-aware input is converted straight to UTC.
    None passes through unchanged.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_DALLAS_TZ)
    return dt.astimezone(timezone.utc)

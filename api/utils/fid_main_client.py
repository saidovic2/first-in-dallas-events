"""
Notify fid-main to revalidate its ISR cache after an event is published.

fid-main exposes POST /api/revalidate (confirmed: returns 401 on bad secret,
405 on GET). Auth header: x-revalidate-secret. Payload: {"paths": [...]}

Set REVALIDATE_SECRET in Railway env vars. Set the same value as
REVALIDATE_SECRET in the fid-main deployment.

On any failure this function logs loudly but does NOT raise — the event is
already PUBLISHED in the DB; fid-main will pick it up at next ISR tick
(600 s worst case). The Stripe webhook must return 200 regardless.
"""

import logging
import re
import unicodedata

import httpx

from config import settings

logger = logging.getLogger(__name__)

_FID_MAIN_REVALIDATE = f"{settings.FID_MAIN_URL}/api/revalidate"


def _slugify_title(title: str) -> str:
    """Exact replica of fid-main lib/events/slug.ts slugifyTitle()."""
    s = title.lower()
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[̀-ͯ]", "", s)   # strip diacritics
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = s.strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = re.sub(r"^-|-$", "", s)
    return s[:80]


def build_event_slug(event_id: int, title: str) -> str:
    return f"{_slugify_title(title)}-{event_id}"


async def notify_fid_main_event_published(event_id: int, title: str) -> None:
    """POST revalidation paths to fid-main after an event is published."""
    if not settings.REVALIDATE_SECRET:
        logger.warning(
            "REVALIDATE_SECRET not set — skipping fid-main cache revalidation "
            "for event_id=%s. Set the env var to enable instant publish.",
            event_id,
        )
        return

    slug = build_event_slug(event_id, title)
    paths = [
        "/events/",
        f"/events/{slug}/",
        "/",          # homepage sidebar uses upcoming events
    ]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                _FID_MAIN_REVALIDATE,
                json={"paths": paths},
                headers={"x-revalidate-secret": settings.REVALIDATE_SECRET},
            )
        if resp.status_code == 200:
            logger.info(
                "fid-main revalidation triggered for event_id=%s slug=%s paths=%s",
                event_id, slug, paths,
            )
        else:
            logger.error(
                "fid-main revalidation returned HTTP %s for event_id=%s — "
                "event is PUBLISHED in DB; fid-main will pick it up at next ISR tick.",
                resp.status_code, event_id,
            )
    except Exception as exc:
        logger.error(
            "fid-main revalidation request failed for event_id=%s: %s — "
            "event is PUBLISHED in DB; fid-main will pick it up at next ISR tick.",
            event_id, exc,
        )

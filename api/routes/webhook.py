"""
POST /api/stripe/webhook

Handles Stripe Checkout and subscription lifecycle events for fid_events submissions.

HARD REQUIREMENT — cross-account isolation:
  This webhook endpoint is shared with a Stripe account that also serves the
  First in Dallas business directory (product="first_in_dallas"). The FIRST
  thing this handler does is check metadata.product. Any event that does not
  carry product="fid_events" is silently returned 200 and ignored.
  This prevents a directory subscription update from touching events flags here.

Handled events:
  checkout.session.completed   → PENDING → PUBLISHED + optional FeaturedSlot
  customer.subscription.updated → logged, no state change
  customer.subscription.deleted → logged; published events stay published
    (organizer loses new-submission ability but existing events are not unpublished)

Every received event type is logged whether processed or skipped.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from config import settings
from database import get_db, SessionLocal
from models.event import Event
from models.featured_slot import FeaturedSlot
from pricing import STRIPE_PRODUCT_TAG, FEATURED_PRICE_USD

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    """
    Stripe webhook endpoint.
    URL: POST https://wonderful-vibrancy-production.up.railway.app/api/stripe/webhook
    Register this URL in the Stripe dashboard with a SEPARATE signing secret
    from the directory's webhook. Set STRIPE_WEBHOOK_SECRET to that secret.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET not configured — cannot verify webhook signature")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    payload = await request.body()

    # ── Verify Stripe signature ───────────────────────────────────────────────
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY.strip()
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET.strip()
        )
    except stripe.SignatureVerificationError:
        logger.warning("Stripe webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")
    except Exception as exc:
        logger.error("Stripe webhook parse error: %s", exc)
        raise HTTPException(status_code=400, detail="Webhook parse error")

    event_type = event["type"]
    logger.info("Stripe webhook received: type=%s id=%s", event_type, event["id"])

    # ── Route by event type ───────────────────────────────────────────────────
    if event_type == "checkout.session.completed":
        published_event_id = _handle_checkout_completed(event["data"]["object"], db)
        if published_event_id:
            background_tasks.add_task(_publish_to_wordpress_background, published_event_id)
            background_tasks.add_task(_notify_fid_main_background, published_event_id)

    elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        _handle_subscription_event(event_type, event["data"]["object"])

    else:
        logger.info("Stripe webhook: unhandled event type %r — returning 200", event_type)

    return {"status": "ok"}


# ── Handlers ──────────────────────────────────────────────────────────────────

def _handle_checkout_completed(session: dict, db: Session) -> int | None:
    """Flip event PENDING → PUBLISHED; create FeaturedSlot if purchased.
    Returns the event_id so the caller can trigger WordPress publish."""
    metadata = session.get("metadata") or {}

    # FIRST CHECK — ignore foreign Stripe events (directory, etc.)
    if metadata.get("product") != STRIPE_PRODUCT_TAG:
        logger.info(
            "checkout.session.completed: ignoring foreign product %r (session=%s)",
            metadata.get("product"), session.get("id"),
        )
        return

    raw_event_id = metadata.get("event_id")
    plan = metadata.get("plan", "single")
    featured = metadata.get("featured", "false").lower() == "true"

    if not raw_event_id:
        logger.error("checkout.session.completed: metadata missing event_id — session=%s", session.get("id"))
        return

    try:
        event_id = int(raw_event_id)
    except ValueError:
        logger.error("checkout.session.completed: non-integer event_id %r", raw_event_id)
        return

    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        logger.error("checkout.session.completed: event_id=%s not found in DB", event_id)
        return

    if db_event.status != "PENDING":
        logger.info(
            "checkout.session.completed: event_id=%s already %s — skipping (idempotent)",
            event_id, db_event.status,
        )
        return

    # ── Atomic write: publish + optional featured slot ────────────────────────
    try:
        db_event.status = "PUBLISHED"

        if featured:
            now = datetime.now(timezone.utc)
            slot = FeaturedSlot(
                event_id=event_id,
                slot_position=1,           # position 1 = highest priority (PLATINUM)
                tier="PLATINUM",
                price_paid=Decimal(str(FEATURED_PRICE_USD)),
                payment_frequency="ONE_TIME",
                starts_at=now,
                ends_at=db_event.start_at,  # slot expires when the event itself starts
                payment_status="PAID",
                payment_method="STRIPE",
                notes=f"Stripe session {session.get('id')}",
                is_active=True,
            )
            db.add(slot)

        db.commit()
        logger.info(
            "checkout.session.completed: event_id=%s published; featured=%s plan=%s",
            event_id, featured, plan,
        )
        return event_id  # caller will trigger WP publish as background task

    except Exception as exc:
        db.rollback()
        logger.error(
            "checkout.session.completed: DB write failed for event_id=%s — rolled back: %s",
            event_id, exc,
        )
        raise HTTPException(status_code=500, detail="DB write failed — Stripe will retry")


async def _publish_to_wordpress_background(event_id: int) -> None:
    """Background task: publish paid event to WordPress and save wp_post_id."""
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            logger.error("WP background publish: event_id=%s not found", event_id)
            return
        if event.wp_post_id:
            logger.info("WP background publish: event_id=%s already has wp_post_id=%s", event_id, event.wp_post_id)
            return
        from utils.wordpress import publish_to_wordpress
        wp_post_id = await publish_to_wordpress(event, auto_enhance=True)
        event.wp_post_id = wp_post_id
        db.commit()
        logger.info("WP background publish: event_id=%s → wp_post_id=%s", event_id, wp_post_id)
    except Exception as exc:
        logger.error("WP background publish failed for event_id=%s: %s", event_id, exc)
    finally:
        db.close()


async def _notify_fid_main_background(event_id: int) -> None:
    """Background task: bust fid-main ISR cache after event is published."""
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            logger.error("fid-main notify: event_id=%s not found", event_id)
            return
        from utils.fid_main_client import notify_fid_main_event_published
        await notify_fid_main_event_published(event_id, event.title)
    except Exception as exc:
        logger.error("fid-main notify background failed for event_id=%s: %s", event_id, exc)
    finally:
        db.close()


def _handle_subscription_event(event_type: str, subscription: dict) -> None:
    """
    Log subscription lifecycle events.

    On cancellation (customer.subscription.deleted):
      Organizer loses the ability to submit new events under the unlimited plan.
      Already-PUBLISHED events are NOT unpublished — they remain live.
      To submit new events they must resubscribe.

    All field accesses are guarded because missing fields on subscription objects
    have crashed webhook handlers before (see directory webhook incident history).
    """
    # Guard every access — subscription object shape can vary by Stripe API version
    sub_id = subscription.get("id", "<unknown>")
    sub_status = subscription.get("status", "<unknown>")
    sub_metadata = {}
    try:
        sub_metadata = subscription.get("metadata") or {}
    except Exception:
        pass

    # FIRST CHECK — ignore foreign subscriptions
    if sub_metadata.get("product") != STRIPE_PRODUCT_TAG:
        logger.info(
            "%s: ignoring foreign subscription product=%r sub=%s",
            event_type, sub_metadata.get("product"), sub_id,
        )
        return

    if event_type == "customer.subscription.deleted":
        logger.info(
            "customer.subscription.deleted: sub=%s status=%s — "
            "organizer loses new-submission access; existing PUBLISHED events unchanged",
            sub_id, sub_status,
        )
    elif event_type == "customer.subscription.updated":
        current_period_end = None
        try:
            current_period_end = subscription.get("current_period_end")
        except Exception:
            pass
        logger.info(
            "customer.subscription.updated: sub=%s status=%s period_end=%s",
            sub_id, sub_status, current_period_end,
        )

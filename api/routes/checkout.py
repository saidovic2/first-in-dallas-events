"""
POST /api/checkout/session

Creates ONE Stripe Checkout session for a paid event submission.
The user reaches Stripe exactly once; featured is a line item, not a second charge.

Four combinations:
  single alone       → mode='payment',      1 line item  ($19)
  single + featured  → mode='payment',      2 line items ($19 + $29)
  unlimited alone    → mode='subscription', 1 line item  ($49/mo)
  unlimited+featured → mode='subscription', 2 line items ($49/mo + $29 one-time)

All sessions are tagged metadata.product='fid_events' so the webhook can
ignore events from the directory's Stripe account.
"""

import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.event import Event
from pricing import STRIPE_PRODUCT_TAG, SINGLE_PRICE_USD, FEATURED_PRICE_USD, UNLIMITED_PRICE_USD

logger = logging.getLogger(__name__)
router = APIRouter()


class CheckoutRequest(BaseModel):
    plan: str       # 'single' | 'unlimited'
    featured: bool = False
    event_id: int


@router.post("/session")
async def create_checkout_session(
    req: CheckoutRequest,
    db: Session = Depends(get_db),
):
    """Build one Stripe Checkout Session for the given plan + optional featured add-on."""

    # ── Validate inputs ───────────────────────────────────────────────────────
    if req.plan not in ("single", "unlimited"):
        raise HTTPException(status_code=400, detail="plan must be 'single' or 'unlimited'")

    event = db.query(Event).filter(Event.id == req.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Event {req.event_id} not found")
    if event.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Event {req.event_id} must be PENDING to start checkout (current: {event.status})",
        )

    # ── Stripe key check ──────────────────────────────────────────────────────
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured on this server")

    required_price_ids = {
        "STRIPE_PRICE_SINGLE": settings.STRIPE_PRICE_SINGLE,
        "STRIPE_PRICE_UNLIMITED": settings.STRIPE_PRICE_UNLIMITED,
        "STRIPE_PRICE_FEATURED": settings.STRIPE_PRICE_FEATURED,
    }
    missing = [k for k, v in required_price_ids.items() if not v]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Stripe Price IDs not configured: {missing}. "
                   "Set price_... IDs (not prod_... Product IDs) in env vars.",
        )

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # ── Build line items ──────────────────────────────────────────────────────
    line_items = []

    if req.plan == "single":
        line_items.append({"price": settings.STRIPE_PRICE_SINGLE, "quantity": 1})
    else:  # unlimited subscription
        line_items.append({"price": settings.STRIPE_PRICE_UNLIMITED, "quantity": 1})

    if req.featured:
        line_items.append({"price": settings.STRIPE_PRICE_FEATURED, "quantity": 1})

    # ── Mode: subscription if unlimited, payment if single ────────────────────
    # Stripe supports mixing a recurring price + one-time price in mode='subscription'.
    # The one-time featured item is charged with the first subscription payment.
    mode = "subscription" if req.plan == "unlimited" else "payment"

    # ── Session metadata — product tag is NON-NEGOTIABLE ─────────────────────
    session_metadata = {
        "product": STRIPE_PRODUCT_TAG,   # "fid_events" — webhook guards on this
        "event_id": str(req.event_id),
        "plan": req.plan,
        "featured": "true" if req.featured else "false",
    }

    # ── Build session kwargs ──────────────────────────────────────────────────
    session_kwargs: dict = {
        "mode": mode,
        "line_items": line_items,
        "metadata": session_metadata,
        "success_url": (
            f"{settings.HUB_URL}/submit/success"
            f"?session_id={{CHECKOUT_SESSION_ID}}&event_id={req.event_id}"
        ),
        "cancel_url": f"{settings.HUB_URL}/submit/cancel?event_id={req.event_id}",
    }

    # For subscription sessions, also tag the subscription object itself so that
    # future lifecycle events (customer.subscription.updated/deleted) carry the
    # product tag and can be filtered correctly by the webhook.
    if mode == "subscription":
        session_kwargs["subscription_data"] = {"metadata": session_metadata}

    # ── Create session ────────────────────────────────────────────────────────
    try:
        session = stripe.checkout.Session.create(**session_kwargs)
    except stripe.error.StripeError as exc:
        logger.error("Stripe session creation failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Stripe error: {exc.user_message or str(exc)}")

    logger.info(
        "Checkout session created: session=%s event_id=%s plan=%s featured=%s",
        session.id, req.event_id, req.plan, req.featured,
    )

    return {
        "checkout_url": session.url,
        "session_id": session.id,
        # Display totals for the UI (informational — Stripe is authoritative)
        "display": {
            "plan": req.plan,
            "plan_price_usd": SINGLE_PRICE_USD if req.plan == "single" else UNLIMITED_PRICE_USD,
            "featured": req.featured,
            "featured_price_usd": FEATURED_PRICE_USD if req.featured else 0,
        },
    }

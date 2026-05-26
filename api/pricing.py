"""
Pricing constants for the FiD Events paid submission wizard.

All monetary display values are in USD. Stripe amounts are in cents.
To change a price, edit ONE value here — never hardcode amounts in route handlers.

Products:
  single     — $19 one-time   — one submission, PENDING → PUBLISHED on payment
  unlimited  — $49/mo         — subscription, unlimited submissions while active
  featured   — $29 one-time   — adds top-of-calendar FeaturedSlot to any submission

Out of scope (step 3):
  newsletter — $99 one-time   — manual fulfillment; NOT wired here
"""

# ── Display prices (USD) ──────────────────────────────────────────────────────
SINGLE_PRICE_USD = 19
UNLIMITED_PRICE_USD = 49
FEATURED_PRICE_USD = 29

# ── Stripe amounts (cents) ────────────────────────────────────────────────────
SINGLE_AMOUNT_CENTS = SINGLE_PRICE_USD * 100      # 1900
UNLIMITED_AMOUNT_CENTS = UNLIMITED_PRICE_USD * 100  # 4900
FEATURED_AMOUNT_CENTS = FEATURED_PRICE_USD * 100    # 2900

# ── Stripe metadata tag ───────────────────────────────────────────────────────
# Every Stripe object this repo creates MUST carry this tag so the webhook can
# distinguish our events from the directory's (product="first_in_dallas").
STRIPE_PRODUCT_TAG = "fid_events"

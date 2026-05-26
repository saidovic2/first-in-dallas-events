import logging

from pydantic import BaseModel, HttpUrl, ValidationInfo, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal

_PRICE_TIER_MAP = {
    'free':     'free',
    'paid':     'paid',
    'donation': 'free',
    'premium':  'paid',
}

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: Optional[datetime] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    price_tier: str = "free"
    price_amount: Optional[Decimal] = None
    image_url: Optional[str] = None
    source_url: str
    source_type: str
    category: Optional[str] = None
    fid_hash: str
    status: str = "draft"

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    price_tier: Optional[str] = None
    price_amount: Optional[Decimal] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_at: datetime
    end_at: Optional[datetime]
    venue: str = ""
    address: str = ""
    city: str = ""
    price_tier: str
    price_amount: Optional[Decimal]
    image_url: Optional[str]
    source_url: str
    source_type: str
    category: Optional[str]
    fid_hash: str
    status: str
    wp_post_id: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('venue', 'address', 'city', mode='before')
    @classmethod
    def coerce_none_to_empty_string(cls, v: Optional[str]) -> str:
        return "" if v is None else v

    @field_validator('price_tier', mode='before')
    @classmethod
    def normalize_price_tier(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return 'paid'
        normalized = _PRICE_TIER_MAP.get(str(v).lower())
        if normalized is None:
            event_id = (info.data or {}).get('id', '?')
            logging.warning(
                "EventResponse: unrecognized price_tier %r for event id=%s, falling back to 'paid'",
                v, event_id,
            )
            return 'paid'
        return normalized

    class Config:
        from_attributes = True

class EventFilter(BaseModel):
    status: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    price_tier: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None
    limit: int = 50
    offset: int = 0

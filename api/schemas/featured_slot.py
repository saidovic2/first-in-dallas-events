from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

# ===============================
# Featured Slot Schemas
# ===============================

class FeaturedSlotBase(BaseModel):
    event_id: int
    slot_position: int = Field(..., ge=1, le=4, description="1=Platinum, 2=Gold, 3=Silver, 4=Bronze")
    tier: str = Field(..., pattern="^(PLATINUM|GOLD|SILVER|BRONZE)$")
    price_paid: Decimal
    payment_frequency: str = Field(default="WEEKLY", pattern="^(ONE_TIME|WEEKLY|MONTHLY|QUARTERLY|YEARLY)$")
    starts_at: datetime
    ends_at: datetime
    payment_status: str = Field(default="PAID", pattern="^(PENDING|PAID|FAILED|REFUNDED|EXPIRED)$")
    payment_method: Optional[str] = "MANUAL"
    notes: Optional[str] = None


class FeaturedSlotCreate(FeaturedSlotBase):
    """Create a new featured slot"""
    pass


class FeaturedSlotUpdate(BaseModel):
    """Update featured slot details"""
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    payment_status: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class FeaturedSlotResponse(FeaturedSlotBase):
    """Featured slot with full details"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ===============================
# Featured Pricing Schemas
# ===============================

class FeaturedPricingResponse(BaseModel):
    """Pricing tier information"""
    id: int
    tier: str
    slot_position: int
    base_price_weekly: Decimal
    discount_monthly: int
    discount_quarterly: int
    discount_yearly: int
    description: Optional[str]
    features: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class PriceCalculation(BaseModel):
    """Calculate price with discounts"""
    tier: str
    frequency: str
    weeks: int = Field(..., gt=0)


class PriceCalculationResponse(BaseModel):
    """Calculated price result"""
    tier: str
    slot_position: int
    frequency: str
    weeks: int
    base_price_weekly: Decimal
    discount_percent: int
    discount_amount: Decimal
    total_price: Decimal
    price_per_week: Decimal


# ===============================
# Featured Event Display
# ===============================

class FeaturedEventDisplay(BaseModel):
    """Featured event for public display"""
    slot_id: int
    slot_position: int
    tier: str
    
    # Event details
    event_id: int
    event_title: str
    event_image: Optional[str]
    event_start: datetime
    event_city: Optional[str]
    event_venue: Optional[str]
    event_description: Optional[str]
    event_source_url: Optional[str]
    event_price_tier: Optional[str]
    event_price_amount: Optional[Decimal]
    
    class Config:
        from_attributes = True


class AvailableSlot(BaseModel):
    """Information about slot availability"""
    slot_position: int
    tier: str
    is_available: bool
    current_event_title: Optional[str] = None
    occupied_until: Optional[datetime] = None
    next_available: Optional[datetime] = None

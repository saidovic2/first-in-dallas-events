from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from database import get_db
from models.event import Event
from models.featured_slot import FeaturedSlot, FeaturedPricing
from schemas.featured_slot import (
    FeaturedSlotCreate,
    FeaturedSlotUpdate,
    FeaturedSlotResponse,
    FeaturedPricingResponse,
    PriceCalculation,
    PriceCalculationResponse,
    FeaturedEventDisplay,
    AvailableSlot
)
from utils.auth import get_current_user
from models.user import User

router = APIRouter()


# ===============================
# PUBLIC ENDPOINTS
# ===============================

@router.get("/pricing", response_model=List[FeaturedPricingResponse])
async def get_featured_pricing(db: Session = Depends(get_db)):
    """Get all featured slot pricing tiers"""
    pricing = db.query(FeaturedPricing).filter(
        FeaturedPricing.is_active == True
    ).order_by(FeaturedPricing.slot_position).all()
    
    return pricing


@router.post("/pricing/calculate", response_model=PriceCalculationResponse)
async def calculate_featured_price(
    calc: PriceCalculation,
    db: Session = Depends(get_db)
):
    """Calculate price for a featured slot with discounts"""
    
    # Get pricing tier
    pricing = db.query(FeaturedPricing).filter(
        FeaturedPricing.tier == calc.tier,
        FeaturedPricing.is_active == True
    ).first()
    
    if not pricing:
        raise HTTPException(status_code=404, detail=f"Pricing tier '{calc.tier}' not found")
    
    # Calculate base cost
    base_total = pricing.base_price_weekly * calc.weeks
    
    # Apply frequency discount
    discount_percent = 0
    if calc.frequency == "MONTHLY" and calc.weeks >= 4:
        discount_percent = pricing.discount_monthly
    elif calc.frequency == "QUARTERLY" and calc.weeks >= 12:
        discount_percent = pricing.discount_quarterly
    elif calc.frequency == "YEARLY" and calc.weeks >= 52:
        discount_percent = pricing.discount_yearly
    
    # Calculate final price
    discount_amount = base_total * (Decimal(discount_percent) / 100)
    total_price = base_total - discount_amount
    price_per_week = total_price / calc.weeks
    
    return PriceCalculationResponse(
        tier=calc.tier,
        slot_position=pricing.slot_position,
        frequency=calc.frequency,
        weeks=calc.weeks,
        base_price_weekly=pricing.base_price_weekly,
        discount_percent=discount_percent,
        discount_amount=discount_amount,
        total_price=total_price,
        price_per_week=price_per_week
    )


@router.get("/active", response_model=List[FeaturedEventDisplay])
async def get_active_featured_events(db: Session = Depends(get_db)):
    """Get currently active featured events for display"""
    
    now = datetime.now(timezone.utc)
    
    # Query active featured slots with their events
    featured = db.query(
        FeaturedSlot.id.label("slot_id"),
        FeaturedSlot.slot_position,
        FeaturedSlot.tier,
        Event.id.label("event_id"),
        Event.title.label("event_title"),
        Event.image_url.label("event_image"),
        Event.start_at.label("event_start"),
        Event.city.label("event_city"),
        Event.venue.label("event_venue"),
        Event.description.label("event_description"),
        Event.source_url.label("event_source_url"),
        Event.price_tier.label("event_price_tier"),
        Event.price_amount.label("event_price_amount")
    ).join(
        Event, FeaturedSlot.event_id == Event.id
    ).filter(
        FeaturedSlot.is_active == True,
        FeaturedSlot.payment_status == "PAID",
        FeaturedSlot.starts_at <= now,
        FeaturedSlot.ends_at >= now,
        Event.status == "PUBLISHED",
        Event.start_at >= now
    ).order_by(
        FeaturedSlot.slot_position
    ).all()
    
    return [
        FeaturedEventDisplay(
            slot_id=row.slot_id,
            slot_position=row.slot_position,
            tier=row.tier,
            event_id=row.event_id,
            event_title=row.event_title,
            event_image=row.event_image,
            event_start=row.event_start,
            event_city=row.event_city,
            event_venue=row.event_venue,
            event_description=row.event_description,
            event_source_url=row.event_source_url,
            event_price_tier=row.event_price_tier,
            event_price_amount=row.event_price_amount
        )
        for row in featured
    ]


@router.get("/availability", response_model=List[AvailableSlot])
async def check_slot_availability(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """Check which slots are available for a date range"""
    
    all_positions = [1, 2, 3, 4]
    pricing = db.query(FeaturedPricing).filter(
        FeaturedPricing.is_active == True
    ).all()
    pricing_map = {p.slot_position: p.tier for p in pricing}
    
    result = []
    
    for position in all_positions:
        # Check if slot is occupied during requested period
        occupied = db.query(FeaturedSlot).join(Event).filter(
            FeaturedSlot.slot_position == position,
            FeaturedSlot.is_active == True,
            FeaturedSlot.payment_status.in_(["PAID", "PENDING"]),
            or_(
                and_(FeaturedSlot.starts_at <= start_date, FeaturedSlot.ends_at >= start_date),
                and_(FeaturedSlot.starts_at <= end_date, FeaturedSlot.ends_at >= end_date),
                and_(FeaturedSlot.starts_at >= start_date, FeaturedSlot.ends_at <= end_date)
            )
        ).first()
        
        if occupied:
            result.append(AvailableSlot(
                slot_position=position,
                tier=pricing_map.get(position, "UNKNOWN"),
                is_available=False,
                current_event_title=occupied.event.title if occupied.event else None,
                occupied_until=occupied.ends_at,
                next_available=occupied.ends_at + timedelta(seconds=1)
            ))
        else:
            result.append(AvailableSlot(
                slot_position=position,
                tier=pricing_map.get(position, "UNKNOWN"),
                is_available=True,
                next_available=start_date
            ))
    
    return result


# ===============================
# ADMIN ENDPOINTS (Protected)
# ===============================

@router.post("/", response_model=FeaturedSlotResponse, status_code=201)
async def create_featured_slot(
    slot: FeaturedSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new featured slot (admin only)"""
    
    # Verify event exists
    event = db.query(Event).filter(Event.id == slot.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if slot is available
    conflicts = db.query(FeaturedSlot).filter(
        FeaturedSlot.slot_position == slot.slot_position,
        FeaturedSlot.is_active == True,
        FeaturedSlot.payment_status.in_(["PAID", "PENDING"]),
        or_(
            and_(FeaturedSlot.starts_at <= slot.starts_at, FeaturedSlot.ends_at >= slot.starts_at),
            and_(FeaturedSlot.starts_at <= slot.ends_at, FeaturedSlot.ends_at >= slot.ends_at),
            and_(FeaturedSlot.starts_at >= slot.starts_at, FeaturedSlot.ends_at <= slot.ends_at)
        )
    ).first()
    
    if conflicts:
        raise HTTPException(
            status_code=409,
            detail=f"Slot {slot.slot_position} is already booked during this period"
        )
    
    # Create featured slot
    new_slot = FeaturedSlot(**slot.model_dump())
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)
    
    return new_slot


@router.get("/", response_model=List[FeaturedSlotResponse])
async def list_featured_slots(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all featured slots (admin only)"""
    
    query = db.query(FeaturedSlot)
    
    if not include_inactive:
        query = query.filter(FeaturedSlot.is_active == True)
    
    slots = query.order_by(FeaturedSlot.slot_position, FeaturedSlot.starts_at.desc()).all()
    
    return slots


@router.get("/{slot_id}", response_model=FeaturedSlotResponse)
async def get_featured_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get featured slot details (admin only)"""
    
    slot = db.query(FeaturedSlot).filter(FeaturedSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Featured slot not found")
    
    return slot


@router.put("/{slot_id}", response_model=FeaturedSlotResponse)
async def update_featured_slot(
    slot_id: int,
    updates: FeaturedSlotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update featured slot (admin only)"""
    
    slot = db.query(FeaturedSlot).filter(FeaturedSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Featured slot not found")
    
    # Update fields
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(slot, field, value)
    
    db.commit()
    db.refresh(slot)
    
    return slot


@router.delete("/{slot_id}")
async def delete_featured_slot(
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a featured slot (admin only)"""
    
    slot = db.query(FeaturedSlot).filter(FeaturedSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Featured slot not found")
    
    db.delete(slot)
    db.commit()
    
    return {"message": "Featured slot deleted successfully"}

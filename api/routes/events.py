from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import hashlib
from database import get_db
from models.event import Event
from models.user import User
from schemas.event import EventResponse, EventUpdate, EventCreate
from utils.auth import get_current_user
from utils.wordpress import publish_to_wordpress

class BulkEventIds(BaseModel):
    event_ids: List[int]

router = APIRouter()

@router.get("/", response_model=List[EventResponse])
async def list_events(
    status: Optional[str] = None,
    city: Optional[str] = None,
    category: Optional[str] = None,
    price_tier: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    include_past: bool = False,  # New parameter to include past events
    limit: int = Query(500, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Event)
    
    # AUTOMATICALLY exclude past events (unless include_past=true for admin)
    if not include_past:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        query = query.filter(Event.start_at >= now)
    
    # Apply filters
    if status:
        query = query.filter(Event.status == status)
    if city:
        query = query.filter(Event.city == city)
    if category:
        query = query.filter(Event.category == category)
    if price_tier:
        query = query.filter(Event.price_tier == price_tier)
    if start_date:
        query = query.filter(Event.start_at >= datetime.fromisoformat(start_date.replace('Z', '+00:00')))
    if end_date:
        query = query.filter(Event.start_at <= datetime.fromisoformat(end_date.replace('Z', '+00:00')))
    if search:
        query = query.filter(
            or_(
                Event.title.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%"),
                Event.venue.ilike(f"%{search}%")
            )
        )
    
    # Order by start date (upcoming events first - closest dates at top)
    query = query.order_by(Event.start_at.asc())
    
    # Pagination
    events = query.offset(offset).limit(limit).all()
    
    return [EventResponse.model_validate(event) for event in events]

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    title: str = Body(...),
    primary_url: str = Body(""),
    venue: str = Body(""),
    address: str = Body(""),
    city: str = Body(...),
    start_at: datetime = Body(...),
    end_at: Optional[datetime] = Body(None),
    price_amount: Optional[float] = Body(None),
    price_tier: str = Body("FREE"),
    image_url: str = Body(""),
    description: str = Body(""),
    status: str = Body("PUBLISHED"),
    category: str = Body("STANDARD"),
    source_type: str = Body("ORGANIZER_SUBMISSION"),
    db: Session = Depends(get_db)
):
    """Create a new event (typically from organizer submissions)"""
    
    # Generate fid_hash (unique identifier)
    hash_string = f"{title}{city}{start_at.isoformat()}"
    fid_hash = hashlib.md5(hash_string.encode()).hexdigest()
    
    # Check if event with same hash already exists
    existing = db.query(Event).filter(Event.fid_hash == fid_hash).first()
    if existing:
        raise HTTPException(status_code=409, detail="Event already exists")
    
    # Create new event
    new_event = Event(
        title=title,
        description=description,
        start_at=start_at,
        end_at=end_at,
        venue=venue if venue else None,
        address=address if address else None,
        city=city,
        price_tier=price_tier,
        price_amount=price_amount,
        image_url=image_url if image_url else None,
        source_url=primary_url if primary_url else f"organizer-{fid_hash}",
        source_type=source_type,
        category=category,
        fid_hash=fid_hash,
        status=status
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return EventResponse.model_validate(new_event)

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse.model_validate(event)

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update fields
    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    
    return EventResponse.model_validate(event)

@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}

# Bulk operations MUST come before /{event_id} routes
@router.post("/bulk/publish")
async def bulk_publish_events(
    body: BulkEventIds,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk publish multiple events to public directory"""
    event_ids = body.event_ids
    if not event_ids:
        raise HTTPException(status_code=400, detail="No event IDs provided")
    
    events = db.query(Event).filter(Event.id.in_(event_ids)).all()
    if not events:
        raise HTTPException(status_code=404, detail="No events found")
    
    published_count = 0
    for event in events:
        try:
            event.status = "PUBLISHED"
            published_count += 1
        except Exception as e:
            print(f"Error publishing event {event.id}: {e}")
            continue
    
    db.commit()
    
    return {
        "message": f"Successfully published {published_count} events",
        "published_count": published_count,
        "total_requested": len(event_ids)
    }

@router.post("/bulk/delete")
async def bulk_delete_events(
    body: BulkEventIds,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Bulk delete multiple events"""
    event_ids = body.event_ids
    if not event_ids:
        raise HTTPException(status_code=400, detail="No event IDs provided")
    
    deleted_count = db.query(Event).filter(Event.id.in_(event_ids)).delete(synchronize_session=False)
    db.commit()
    
    return {
        "message": f"Successfully deleted {deleted_count} events",
        "deleted_count": deleted_count
    }

@router.post("/{event_id}/publish")
async def publish_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    try:
        wp_post_id = await publish_to_wordpress(event)
        event.wp_post_id = wp_post_id
        event.status = "published"
        db.commit()
        
        return {"message": "Event published to WordPress", "wp_post_id": wp_post_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish: {str(e)}")

@router.get("/cities/list")
async def list_cities(db: Session = Depends(get_db)):
    cities = db.query(Event.city).distinct().filter(Event.city.isnot(None)).all()
    return [city[0] for city in cities if city[0]]

@router.get("/categories/list")
async def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Event.category).distinct().filter(Event.category.isnot(None)).all()
    return [cat[0] for cat in categories if cat[0]]

@router.post("/cleanup/past-events")
async def cleanup_past_events(
    days_old: int = Query(7, description="Delete events older than X days after their start date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete events that have already passed.
    By default, deletes events that ended more than 7 days ago.
    """
    from datetime import datetime, timezone, timedelta
    
    # Calculate cutoff date (now - days_old)
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
    
    # Find past events
    past_events = db.query(Event).filter(Event.start_at < cutoff_date).all()
    deleted_count = len(past_events)
    
    # Delete them
    for event in past_events:
        db.delete(event)
    
    db.commit()
    
    return {
        "message": f"Deleted {deleted_count} past events",
        "deleted_count": deleted_count,
        "cutoff_date": cutoff_date.isoformat()
    }

"""
Ticketmaster API Routes
Endpoints for fetching and importing Ticketmaster events
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Event, User
from routes.auth import get_current_user
from services.ticketmaster import TicketmasterService
from datetime import datetime

router = APIRouter()
tm_service = TicketmasterService()


@router.get("/search")
async def search_ticketmaster_events(
    city: str = Query("Dallas", description="City name"),
    state_code: str = Query("TX", description="State code"),
    keyword: Optional[str] = None,
    classification: Optional[str] = None,
    size: int = Query(20, le=200),
    page: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """
    Search for events on Ticketmaster
    
    **Requires authentication**
    """
    results = tm_service.search_events(
        city=city,
        state_code=state_code,
        keyword=keyword,
        classification=classification,
        size=size,
        page=page
    )
    
    if "error" in results:
        raise HTTPException(status_code=500, detail=results["error"])
    
    # Extract events
    events = results.get("_embedded", {}).get("events", [])
    page_info = results.get("page", {})
    
    return {
        "events": events,
        "total": page_info.get("totalElements", 0),
        "page": page_info.get("number", 0),
        "size": page_info.get("size", 20),
        "total_pages": page_info.get("totalPages", 0)
    }


@router.get("/event/{event_id}")
async def get_ticketmaster_event(
    event_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific Ticketmaster event
    
    **Requires authentication**
    """
    event = tm_service.get_event_details(event_id)
    
    if "error" in event:
        raise HTTPException(status_code=500, detail=event["error"])
    
    return event


@router.post("/import/{event_id}")
async def import_ticketmaster_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import a Ticketmaster event into your local database
    
    **Requires authentication**
    """
    # Check if event already exists
    existing = db.query(Event).filter(Event.external_id == event_id).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Event already imported: {existing.title}"
        )
    
    # Fetch event from Ticketmaster
    tm_event = tm_service.get_event_details(event_id)
    if "error" in tm_event:
        raise HTTPException(status_code=500, detail=tm_event["error"])
    
    # Transform to local format
    local_event_data = tm_service.transform_to_local_event(tm_event)
    
    # Create database record
    new_event = Event(**local_event_data)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return {
        "message": f"Successfully imported: {new_event.title}",
        "event_id": new_event.id,
        "title": new_event.title
    }


@router.post("/bulk-import")
async def bulk_import_ticketmaster_events(
    city: str = Query("Dallas"),
    state_code: str = Query("TX"),
    classification: Optional[str] = None,
    max_events: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk import multiple Ticketmaster events at once
    
    **Requires authentication**
    """
    # Search for events
    results = tm_service.search_events(
        city=city,
        state_code=state_code,
        classification=classification,
        size=max_events
    )
    
    if "error" in results:
        raise HTTPException(status_code=500, detail=results["error"])
    
    events = results.get("_embedded", {}).get("events", [])
    
    imported_count = 0
    skipped_count = 0
    errors = []
    
    for tm_event in events:
        try:
            event_id = tm_event.get("id")
            
            # Check if already exists
            existing = db.query(Event).filter(Event.external_id == event_id).first()
            if existing:
                skipped_count += 1
                continue
            
            # Transform and import
            local_event_data = tm_service.transform_to_local_event(tm_event)
            new_event = Event(**local_event_data)
            db.add(new_event)
            db.commit()
            
            imported_count += 1
            
        except Exception as e:
            errors.append(f"{tm_event.get('name', 'Unknown')}: {str(e)}")
            continue
    
    return {
        "message": f"Bulk import complete",
        "imported": imported_count,
        "skipped": skipped_count,
        "total_found": len(events),
        "errors": errors
    }

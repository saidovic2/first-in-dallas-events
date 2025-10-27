from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from database import get_db
from models.event import Event
from models.user import User
from utils.auth import get_current_user

router = APIRouter()

class EventSubmissionCreate(BaseModel):
    title: str
    primary_url: Optional[str] = None
    format: str
    country: str = "USA"
    venue: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    price: Optional[float] = None
    price_tier: str = "free"
    image_url: Optional[str] = None
    description: Optional[str] = None
    organizer_contact: Optional[str] = None
    submission_type: str = "free"
    organizer_id: str
    organizer_email: str

@router.post("/")
async def create_submission(
    submission: EventSubmissionCreate,
    db: Session = Depends(get_db)
):
    """Create new event submission from organizer portal"""
    try:
        # Create event with PENDING status
        event = Event(
            title=submission.title,
            source_url=submission.primary_url,
            venue=submission.venue,
            address=submission.address,
            city=submission.city,
            state=submission.state,
            start_at=datetime.fromisoformat(submission.start_date.replace('Z', '+00:00')),
            end_at=datetime.fromisoformat(submission.end_date.replace('Z', '+00:00')) if submission.end_date else None,
            price_amount=submission.price,
            price_tier=submission.price_tier.upper(),
            image_url=submission.image_url,
            description=submission.description,
            status="PENDING",  # Submissions start as PENDING
            source_type="organizer_submission",
            category=submission.submission_type.upper()  # Store FREE or PAID in category
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return {
            "id": event.id,
            "status": "pending",
            "message": "Event submission received! We'll review it shortly."
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create submission: {str(e)}")

@router.get("/by-organizer/{organizer_id}")
async def get_organizer_submissions(
    organizer_id: str,
    db: Session = Depends(get_db)
):
    """Get all submissions for an organizer (by organizer_id from Supabase)"""
    # Since we don't have organizer_id column in events table yet,
    # return all organizer submissions for now
    events = db.query(Event).filter(
        Event.source_type == "organizer_submission"
    ).order_by(Event.created_at.desc()).all()
    
    return events

@router.patch("/{submission_id}/approve")
async def approve_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin approves submission and publishes it"""
    event = db.query(Event).filter(Event.id == submission_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if event.status != "PENDING":
        raise HTTPException(status_code=400, detail="Only pending submissions can be approved")
    
    event.status = "PUBLISHED"
    db.commit()
    
    return {
        "message": "Event approved and published",
        "event_id": event.id
    }

@router.patch("/{submission_id}/reject")
async def reject_submission(
    submission_id: int,
    reason: str = Query(..., description="Reason for rejection"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin rejects submission with reason"""
    event = db.query(Event).filter(Event.id == submission_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if event.status != "PENDING":
        raise HTTPException(status_code=400, detail="Only pending submissions can be rejected")
    
    event.status = "REJECTED"
    # Note: Add admin_notes field to Event model if you want to store rejection reason
    db.commit()
    
    return {
        "message": "Event rejected",
        "event_id": event.id,
        "reason": reason
    }

@router.get("/pending")
async def get_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending submissions for admin review"""
    events = db.query(Event).filter(
        Event.status == "PENDING",
        Event.source_type == "organizer_submission"
    ).order_by(Event.created_at.desc()).all()
    
    return events

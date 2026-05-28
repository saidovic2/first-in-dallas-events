import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from database import get_db
from models.event import Event

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
        # Stable dedup hash for organizer submissions
        fid_hash = hashlib.md5(
            f"{submission.title}{submission.start_date}{submission.organizer_id}".encode()
        ).hexdigest()

        # Idempotent: if this exact submission already exists as PENDING, return it
        existing = db.query(Event).filter(Event.fid_hash == fid_hash).first()
        if existing:
            return {
                "id": existing.id,
                "status": existing.status.lower(),
                "message": "Existing submission found.",
            }

        event = Event(
            title=submission.title,
            source_url=submission.primary_url or "",   # NOT NULL — default empty when no URL
            venue=submission.venue,
            address=submission.address,
            city=submission.city,
            start_at=datetime.fromisoformat(submission.start_date.replace('Z', '+00:00')),
            end_at=datetime.fromisoformat(submission.end_date.replace('Z', '+00:00')) if submission.end_date else None,
            price_amount=submission.price,
            price_tier=submission.price_tier.lower(),  # Enum values are lowercase: "free"/"paid"
            image_url=submission.image_url,
            description=submission.description,
            status="PENDING",   # Submissions start PENDING; payment webhook flips to PUBLISHED
            source_type="organizer_submission",
            fid_hash=fid_hash,
            organizer_id=submission.organizer_id,
            organizer_email=submission.organizer_email,
            # category intentionally NOT set from submission_type — organizers can set it later
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

@router.get("/{submission_id}/")
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Get a single submission by ID (used by hub success page to poll for PUBLISHED status)"""
    event = db.query(Event).filter(Event.id == submission_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"id": event.id, "status": event.status, "title": event.title}


@router.get("/by-organizer/{organizer_id}")
async def get_organizer_submissions(
    organizer_id: str,
    db: Session = Depends(get_db)
):
    """Get all submissions for an organizer (filtered by Supabase user ID)"""
    events = db.query(Event).filter(
        Event.source_type == "organizer_submission",
        Event.organizer_id == organizer_id,
    ).order_by(Event.created_at.desc()).all()

    return [
        {
            "id": e.id,
            "title": e.title,
            "city": e.city,
            "venue": e.venue,
            "description": e.description,
            "start_at": e.start_at.isoformat() if e.start_at else None,
            "end_at": e.end_at.isoformat() if e.end_at else None,
            "status": e.status.lower(),   # normalize: "PUBLISHED" → "published"
            "source_url": e.source_url,
            "image_url": e.image_url,
            "price_tier": e.price_tier,
            "is_featured": e.is_featured,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]

@router.patch("/{submission_id}/approve")
async def approve_submission(
    submission_id: int,
    db: Session = Depends(get_db),
):
    """Admin approves submission and publishes it"""
    event = db.query(Event).filter(Event.id == submission_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if event.status != "PENDING":
        raise HTTPException(status_code=400, detail="Only pending submissions can be approved")
    
    event.status = "PUBLISHED"
    db.commit()
    db.refresh(event)
    
    # Auto-publish to WordPress
    try:
        from utils.wordpress import publish_to_wordpress
        print(f"📝 Auto-publishing approved submission to WordPress: {event.title}")
        wp_post_id = await publish_to_wordpress(event, auto_enhance=True)
        
        # Save WordPress post ID back to event
        event.wp_post_id = wp_post_id
        db.commit()
        
        print(f"✅ WordPress post created (ID: {wp_post_id})")
    except Exception as e:
        # Don't fail approval if WordPress publish fails
        print(f"⚠️ WordPress auto-publish failed: {e}")
        # Event still approved successfully, just without WordPress post
    
    return {
        "message": "Event approved and published to WordPress",
        "event_id": event.id,
        "wp_post_id": event.wp_post_id
    }

@router.patch("/{submission_id}/reject")
async def reject_submission(
    submission_id: int,
    reason: str = Query(..., description="Reason for rejection"),
    db: Session = Depends(get_db),
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

@router.get("/admin/all")
async def get_all_submissions_admin(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all organizer submissions for the admin panel (auth handled by frontend Supabase)"""
    q = db.query(Event).filter(Event.source_type == "organizer_submission")
    if status:
        q = q.filter(Event.status == status.upper())
    events = q.order_by(Event.created_at.desc()).all()

    return [
        {
            "id": e.id,
            "title": e.title,
            "city": e.city,
            "venue": e.venue,
            "address": e.address,
            "description": e.description,
            "start_at": e.start_at.isoformat() if e.start_at else None,
            "end_at": e.end_at.isoformat() if e.end_at else None,
            "status": e.status.lower(),
            "source_url": e.source_url,
            "image_url": e.image_url,
            "price_tier": e.price_tier,
            "price_amount": float(e.price_amount) if e.price_amount else None,
            "is_featured": e.is_featured,
            "organizer_id": e.organizer_id,
            "organizer_email": e.organizer_email,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]


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

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import redis
import json
from database import get_db
from models.user import User
from routes.auth import get_current_user

router = APIRouter()

# Redis connection for task queue
import os
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

@router.post("/eventbrite/dallas")
async def sync_eventbrite_dallas(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk sync Eventbrite events from Dallas-area organizers
    """
    try:
        # Create a bulk sync task
        task_data = {
            "url": "bulk:eventbrite:dallas",
            "source_type": "eventbrite_bulk",
            "status": "queued"
        }
        
        # Add to Redis queue
        task_id = redis_client.incr("task_counter")
        redis_client.lpush("extraction_queue", json.dumps({
            "task_id": task_id,
            **task_data
        }))
        
        # Save task to database
        from models.task import Task
        task = Task(
            url=task_data["url"],
            source_type=task_data["source_type"],
            status=task_data["status"]
        )
        db.add(task)
        db.commit()
        
        return {
            "message": "Eventbrite bulk sync started",
            "task_id": task.id,
            "status": "queued",
            "note": "Configure Eventbrite organizers in settings for more events"
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in sync_eventbrite_dallas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ticketmaster/dallas")
async def sync_ticketmaster_dallas(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk sync Ticketmaster events from Dallas-Fort Worth area
    Includes concerts, sports, theater, and more with affiliate tracking
    """
    try:
        # Create a bulk sync task
        task_data = {
            "url": "bulk:ticketmaster:dallas",
            "source_type": "ticketmaster_bulk",
            "status": "queued"
        }
        
        # Add to Redis queue
        task_id = redis_client.incr("task_counter")
        redis_client.lpush("extraction_queue", json.dumps({
            "task_id": task_id,
            **task_data
        }))
        
        # Save task to database
        from models.task import Task
        task = Task(
            url=task_data["url"],
            source_type=task_data["source_type"],
            status=task_data["status"]
        )
        db.add(task)
        db.commit()
        
        return {
            "message": "Ticketmaster bulk sync started",
            "task_id": task.id,
            "status": "queued",
            "locations": ["Dallas", "Fort Worth", "Arlington", "Plano"],
            "radius": "50 miles",
            "categories": ["Music", "Sports", "Arts & Theatre", "Film"],
            "note": "Events include affiliate tracking for commission earnings"
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in sync_ticketmaster_dallas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dallas-arboretum")
async def sync_dallas_arboretum(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync events from Dallas Arboretum & Botanical Garden
    Focuses on family-friendly and kids events
    """
    try:
        # Create a sync task
        task_data = {
            "url": "bulk:dallas_arboretum",
            "source_type": "dallas_arboretum_bulk",
            "status": "queued"
        }
        
        # Add to Redis queue
        task_id = redis_client.incr("task_counter")
        redis_client.lpush("extraction_queue", json.dumps({
            "task_id": task_id,
            **task_data
        }))
        
        # Save task to database
        from models.task import Task
        task = Task(
            url=task_data["url"],
            source_type=task_data["source_type"],
            status=task_data["status"]
        )
        db.add(task)
        db.commit()
        
        return {
            "message": "Dallas Arboretum sync started",
            "task_id": task.id,
            "status": "queued",
            "venue": "Dallas Arboretum & Botanical Garden",
            "focus": "Family-friendly and kids events",
            "categories": ["Nature & Gardens", "Family & Kids", "Education", "Holiday"]
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in sync_dallas_arboretum: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/klyde-warren-park")
async def sync_klyde_warren_park(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync events from Klyde Warren Park
    Focuses on family-friendly and community events
    """
    try:
        # Create a sync task
        task_data = {
            "url": "bulk:klyde_warren_park",
            "source_type": "klyde_warren_park_bulk",
            "status": "queued"
        }
        
        # Add to Redis queue
        task_id = redis_client.incr("task_counter")
        redis_client.lpush("extraction_queue", json.dumps({
            "task_id": task_id,
            **task_data
        }))
        
        # Save task to database
        from models.task import Task
        task = Task(
            url=task_data["url"],
            source_type=task_data["source_type"],
            status=task_data["status"]
        )
        db.add(task)
        db.commit()
        
        return {
            "message": "Klyde Warren Park sync started",
            "task_id": task.id,
            "status": "queued",
            "venue": "Klyde Warren Park",
            "focus": "Family-friendly and community events",
            "categories": ["Music & Concerts", "Movies & Film", "Family & Kids", "Food & Dining", "Arts & Theatre"]
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in sync_klyde_warren_park: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of recent bulk sync operations
    """
    try:
        from models.task import Task
        from sqlalchemy import desc
        
        # Get recent bulk sync tasks
        eventbrite_tasks = db.query(Task).filter(
            Task.source_type == "eventbrite_bulk"
        ).order_by(desc(Task.created_at)).limit(5).all()
        
        ticketmaster_tasks = db.query(Task).filter(
            Task.source_type == "ticketmaster_bulk"
        ).order_by(desc(Task.created_at)).limit(5).all()
        
        dallas_arboretum_tasks = db.query(Task).filter(
            Task.source_type == "dallas_arboretum_bulk"
        ).order_by(desc(Task.created_at)).limit(5).all()
        
        klyde_warren_park_tasks = db.query(Task).filter(
            Task.source_type == "klyde_warren_park_bulk"
        ).order_by(desc(Task.created_at)).limit(5).all()
        
        return {
            "eventbrite": [
                {
                    "id": task.id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "logs": task.logs
                }
                for task in eventbrite_tasks
            ],
            "ticketmaster": [
                {
                    "id": task.id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "logs": task.logs
                }
                for task in ticketmaster_tasks
            ],
            "dallas_arboretum": [
                {
                    "id": task.id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "logs": task.logs
                }
                for task in dallas_arboretum_tasks
            ],
            "klyde_warren_park": [
                {
                    "id": task.id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "logs": task.logs
                }
                for task in klyde_warren_park_tasks
            ]
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in get_sync_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

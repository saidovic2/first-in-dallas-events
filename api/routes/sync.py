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

@router.post("/facebook/dallas")
async def sync_facebook_dallas(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk sync Facebook events from Dallas, Plano, Arlington, and Fort Worth
    Uses Apify to search by location
    """
    try:
        # Create a bulk sync task
        task_data = {
            "url": "bulk:facebook:dallas",
            "source_type": "facebook_bulk",
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
            "message": "Facebook bulk sync started",
            "task_id": task.id,
            "status": "queued",
            "locations": ["Dallas, TX", "Plano, TX", "Arlington, TX", "Fort Worth, TX"],
            "estimated_events": "200-400"
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in sync_facebook_dallas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
        facebook_tasks = db.query(Task).filter(
            Task.source_type == "facebook_bulk"
        ).order_by(desc(Task.created_at)).limit(5).all()
        
        eventbrite_tasks = db.query(Task).filter(
            Task.source_type == "eventbrite_bulk"
        ).order_by(desc(Task.created_at)).limit(5).all()
        
        return {
            "facebook": [
                {
                    "id": task.id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "logs": task.logs
                }
                for task in facebook_tasks
            ],
            "eventbrite": [
                {
                    "id": task.id,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "logs": task.logs
                }
                for task in eventbrite_tasks
            ]
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in get_sync_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

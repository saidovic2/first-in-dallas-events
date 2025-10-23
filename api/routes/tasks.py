from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.task import Task
from models.user import User
from schemas.task import TaskCreate, TaskResponse
from utils.auth import get_current_user
from utils.queue import queue_extraction_task
import re

router = APIRouter()

def detect_source_type(url: str) -> str:
    """Detect the type of source from URL"""
    url_lower = url.lower()
    
    if "facebook.com" in url_lower or "fb.com" in url_lower:
        return "facebook"
    elif "instagram.com" in url_lower:
        return "instagram"
    elif url_lower.endswith(".ics") or "ical" in url_lower:
        return "ics"
    elif url_lower.endswith(".xml") or "rss" in url_lower or "feed" in url_lower:
        return "rss"
    else:
        return "webpage"

@router.post("/extract", response_model=List[TaskResponse])
async def create_extraction_tasks(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    created_tasks = []
    
    for url in task_data.urls:
        # Detect source type
        source_type = detect_source_type(url)
        
        # Create task
        task = Task(
            url=url,
            source_type=source_type,
            status="queued"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Queue for processing
        await queue_extraction_task(task.id, url, source_type)
        
        created_tasks.append(TaskResponse.model_validate(task))
    
    return created_tasks

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    
    query = query.order_by(Task.created_at.desc())
    tasks = query.offset(offset).limit(limit).all()
    
    return [TaskResponse.model_validate(task) for task in tasks]

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)

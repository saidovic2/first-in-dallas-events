from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from database import get_db
from models.event import Event
from models.task import Task
from models.source import Source
from models.user import User
from schemas.stats import StatsResponse
from utils.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=StatsResponse)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total events
    total_events = db.query(func.count(Event.id)).scalar()
    
    # Events this week
    week_ago = datetime.now() - timedelta(days=7)
    events_this_week = db.query(func.count(Event.id)).filter(
        Event.created_at >= week_ago
    ).scalar()
    
    # Total extractions (tasks)
    total_extractions = db.query(func.count(Task.id)).scalar()
    
    # Active sources
    active_sources = db.query(func.count(Source.id)).filter(
        Source.status == "active"
    ).scalar()
    
    # Failed tasks
    failed_tasks = db.query(func.count(Task.id)).filter(
        Task.status == "failed"
    ).scalar()
    
    # Extraction success rate
    done_tasks = db.query(func.count(Task.id)).filter(
        Task.status == "done"
    ).scalar()
    extraction_success_rate = (done_tasks / total_extractions * 100) if total_extractions > 0 else 0
    
    # Top sources
    top_sources = db.query(
        Event.source_url,
        func.count(Event.id).label("count")
    ).group_by(Event.source_url).order_by(func.count(Event.id).desc()).limit(5).all()
    
    top_sources_list = [
        {"url": source[0], "count": source[1]}
        for source in top_sources
    ]
    
    # Events by status
    events_by_status_query = db.query(
        Event.status,
        func.count(Event.id).label("count")
    ).group_by(Event.status).all()
    
    events_by_status = {
        status: count for status, count in events_by_status_query
    }
    
    # Events by city
    events_by_city = db.query(
        Event.city,
        func.count(Event.id).label("count")
    ).filter(Event.city.isnot(None)).group_by(Event.city).order_by(
        func.count(Event.id).desc()
    ).limit(10).all()
    
    events_by_city_list = [
        {"city": city, "count": count}
        for city, count in events_by_city
    ]
    
    # Recent errors
    recent_errors = db.query(Task).filter(
        Task.status == "failed"
    ).order_by(Task.updated_at.desc()).limit(5).all()
    
    recent_errors_list = [
        {
            "task_id": task.id,
            "url": task.url,
            "error": task.error_message,
            "timestamp": task.updated_at.isoformat() if task.updated_at else None
        }
        for task in recent_errors
    ]
    
    return StatsResponse(
        total_events=total_events or 0,
        events_this_week=events_this_week or 0,
        total_extractions=total_extractions or 0,
        active_sources=active_sources or 0,
        failed_tasks=failed_tasks or 0,
        extraction_success_rate=round(extraction_success_rate, 2),
        top_sources=top_sources_list,
        events_by_status=events_by_status,
        events_by_city=events_by_city_list,
        recent_errors=recent_errors_list
    )

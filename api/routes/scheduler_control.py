"""
Scheduler Control Endpoints
Manual trigger and status endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from utils.auth import get_current_user
from scheduler import trigger_sync_now, scheduler
from apscheduler.job import Job

router = APIRouter()


@router.post("/trigger")
async def trigger_manual_sync(
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger a sync of all sources now
    Useful for testing or urgent updates
    """
    try:
        import asyncio
        asyncio.create_task(trigger_sync_now())
        
        return {
            "message": "Manual sync triggered",
            "status": "running",
            "note": "Check logs for progress"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_scheduler_status(
    current_user: User = Depends(get_current_user)
):
    """Get scheduler status and upcoming jobs"""
    try:
        jobs = scheduler.get_jobs()
        
        job_info = []
        for job in jobs:
            job_info.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "scheduler_running": scheduler.running,
            "jobs": job_info,
            "job_count": len(jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

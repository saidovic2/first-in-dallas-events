"""
Automated Event Sync & Publish Scheduler
Runs 2x daily: 8 AM and 6 PM Central Time
"""

import os
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import redis
import json
from sqlalchemy.orm import Session
from database import SessionLocal
from models.event import Event
from utils.wordpress import publish_to_wordpress

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Event sources to sync
EVENT_SOURCES = [
    {"name": "Eventbrite Dallas", "type": "eventbrite_bulk", "url": "bulk:eventbrite:dallas"},
    {"name": "Dallas Arboretum", "type": "dallas_arboretum", "url": "https://www.dallasarboretum.org/events-activities/"},
    {"name": "Klyde Warren Park", "type": "klyde_warren", "url": "https://www.klydewarrenpark.org/things-to-do/events.html"},
    {"name": "Perot Museum", "type": "perot_museum", "url": "https://www.perotmuseum.org/explore-the-museum/calendar/index.html"},
    {"name": "Dallas Library", "type": "dallas_library", "url": "https://dallaslibrary2.org/events/"},
    {"name": "Dallas Zoo", "type": "dallas_zoo", "url": "https://www.dallaszoo.com/events/"},
    {"name": "Fair Park", "type": "fair_park", "url": "https://fairpark.org/events/"},
    {"name": "House of Blues", "type": "house_of_blues", "url": "https://www.houseofblues.com/dallas"},
    {"name": "Factory Deep Ellum", "type": "factory_deep_ellum", "url": "https://www.factorydeepellum.com/events"},
]


async def queue_sync_task(source_type: str, url: str, name: str):
    """Queue a sync task in Redis"""
    try:
        task_id = redis_client.incr("task_counter")
        task_data = {
            "task_id": task_id,
            "url": url,
            "source_type": source_type,
            "status": "queued",
            "queued_at": datetime.now().isoformat()
        }
        
        redis_client.lpush("extraction_queue", json.dumps(task_data))
        logger.info(f"✓ Queued sync task for {name} (ID: {task_id})")
        return task_id
        
    except Exception as e:
        logger.error(f"✗ Failed to queue {name}: {e}")
        return None


async def sync_all_sources():
    """Sync all event sources"""
    logger.info("="*80)
    logger.info("🔄 STARTING AUTOMATED SYNC FOR ALL SOURCES")
    logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    logger.info("="*80)
    
    queued_tasks = []
    
    for source in EVENT_SOURCES:
        task_id = await queue_sync_task(
            source["type"],
            source["url"],
            source["name"]
        )
        
        if task_id:
            queued_tasks.append((source["name"], task_id))
        
        # Small delay between tasks
        await asyncio.sleep(2)
    
    logger.info(f"\n✓ Queued {len(queued_tasks)} sync tasks")
    for name, task_id in queued_tasks:
        logger.info(f"  - {name} (Task #{task_id})")
    
    # Wait a bit, then trigger auto-publish
    await asyncio.sleep(300)  # Wait 5 minutes for syncs to complete
    await auto_publish_new_events()


async def auto_publish_new_events():
    """Auto-publish newly imported DRAFT events to WordPress"""
    logger.info("\n" + "="*80)
    logger.info("📤 AUTO-PUBLISHING NEW EVENTS TO WORDPRESS")
    logger.info("="*80)
    
    db = SessionLocal()
    
    try:
        # Get all DRAFT events without wp_post_id (never published)
        new_events = db.query(Event).filter(
            Event.status == "DRAFT",
            Event.wp_post_id == None
        ).limit(50).all()  # Publish max 50 at a time
        
        if not new_events:
            logger.info("✓ No new events to publish")
            return
        
        logger.info(f"📋 Found {len(new_events)} new events to publish")
        
        published_count = 0
        failed_count = 0
        
        for event in new_events:
            try:
                # Publish to WordPress
                wp_post_id = await publish_to_wordpress(event)
                
                if wp_post_id:
                    # Update event status and wp_post_id
                    event.status = "PUBLISHED"
                    event.wp_post_id = wp_post_id
                    db.commit()
                    
                    published_count += 1
                    logger.info(f"  ✓ Published: {event.title[:50]} (WP ID: {wp_post_id})")
                else:
                    failed_count += 1
                    logger.warning(f"  ✗ Failed: {event.title[:50]}")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                failed_count += 1
                logger.error(f"  ✗ Error publishing {event.title[:50]}: {e}")
                db.rollback()
                continue
        
        logger.info(f"\n📊 PUBLISH SUMMARY")
        logger.info(f"  ✓ Published: {published_count}")
        logger.info(f"  ✗ Failed: {failed_count}")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"✗ Auto-publish error: {e}")
        db.rollback()
    finally:
        db.close()


async def cleanup_old_events():
    """Clean up events from yesterday and earlier (Dallas/Central Time)"""
    logger.info("\n🧹 Running maintenance: Cleaning old events...")
    
    db = SessionLocal()
    
    try:
        from datetime import timedelta
        import pytz
        
        # Get current date in Dallas time (Central Time)
        dallas_tz = pytz.timezone('America/Chicago')
        dallas_now = datetime.now(dallas_tz)
        
        # Calculate start of today (midnight) in Dallas time
        start_of_today = dallas_now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Delete events that ended BEFORE today (keep today's events!)
        deleted = db.query(Event).filter(
            Event.start_at < start_of_today
        ).delete()
        
        db.commit()
        logger.info(f"✓ Cleaned up {deleted} events from before today")
        logger.info(f"  Dallas time: {dallas_now.strftime('%Y-%m-%d %I:%M %p %Z')}")
        logger.info(f"  Kept all events from: {start_of_today.strftime('%Y-%m-%d')} onwards")
        
    except Exception as e:
        logger.error(f"✗ Cleanup error: {e}")
        db.rollback()
    finally:
        db.close()


# Initialize scheduler
scheduler = AsyncIOScheduler()


def start_scheduler():
    """Start the automated scheduler"""
    
    # Morning sync: 8 AM Central Time
    scheduler.add_job(
        sync_all_sources,
        CronTrigger(hour=8, minute=0, timezone='America/Chicago'),
        id='morning_sync',
        name='Morning Event Sync (8 AM CT)',
        replace_existing=True
    )
    
    # Evening sync: 6 PM Central Time
    scheduler.add_job(
        sync_all_sources,
        CronTrigger(hour=18, minute=0, timezone='America/Chicago'),
        id='evening_sync',
        name='Evening Event Sync (6 PM CT)',
        replace_existing=True
    )
    
    # Daily cleanup: 2 AM Central Time (removes events before today)
    scheduler.add_job(
        cleanup_old_events,
        CronTrigger(hour=2, minute=0, timezone='America/Chicago'),
        id='daily_cleanup',
        name='Daily Event Cleanup - Keep Today (2 AM CT)',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("="*80)
    logger.info("🚀 AUTOMATED SCHEDULER STARTED")
    logger.info("="*80)
    logger.info("📅 Schedule:")
    logger.info("  - Morning Sync: 8:00 AM Central Time")
    logger.info("  - Evening Sync: 6:00 PM Central Time")
    logger.info("  - Daily Cleanup: 2:00 AM Central Time")
    logger.info("="*80)
    logger.info("\n✓ Scheduler is now running in background...")
    logger.info("✓ Events will auto-sync and publish 2x daily")
    logger.info("✓ No manual intervention needed!\n")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("⏹ Scheduler stopped")


# For manual trigger (testing)
async def trigger_sync_now():
    """Manually trigger sync (for testing)"""
    logger.info("🔄 MANUAL SYNC TRIGGERED")
    await sync_all_sources()

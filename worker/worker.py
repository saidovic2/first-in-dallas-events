import time
import sys
import os
import redis
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors.json_ld import extract_json_ld
from extractors.ics import extract_ics
from extractors.rss import extract_rss
from extractors.html import extract_html_fallback
from extractors.eventbrite import extract_eventbrite_events
from utils.image_uploader import process_event_image

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/events_cms")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_next_task():
    """Get the next task from the queue"""
    task_json = redis_client.rpop("extraction_queue")
    if task_json:
        return json.loads(task_json)
    return None

def update_task_status(db, task_id, status, logs=None, error_message=None, events_extracted=0):
    """Update task status in database"""
    from models.task import Task
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        if logs:
            task.logs = logs
        if error_message:
            task.error_message = error_message
        task.events_extracted = events_extracted
        task.updated_at = datetime.now()
        # Set completed_at when task finishes
        if status in ["done", "failed"]:
            task.completed_at = datetime.now()
        db.commit()

def process_task(task_data):
    """Process a single extraction task"""
    db = SessionLocal()
    task_id = task_data["task_id"]
    url = task_data["url"]
    source_type = task_data["source_type"]
    
    print(f"Processing task {task_id}: {url} ({source_type})")
    
    try:
        # Update status to running
        update_task_status(db, task_id, "running", logs=f"Started processing {url}")
        
        events = []
        
        # Check for bulk sync operations
        if source_type == "eventbrite_bulk" and url == "bulk:eventbrite:dallas":
            # Bulk Eventbrite sync
            from extractors.bulk_eventbrite import bulk_sync_eventbrite_dallas
            events = bulk_sync_eventbrite_dallas()
        elif source_type == "ticketmaster_bulk" and url == "bulk:ticketmaster:dallas":
            # Bulk Ticketmaster sync
            from extractors.ticketmaster import extract_ticketmaster_events
            events = extract_ticketmaster_events(city="Dallas", state="TX")
        elif source_type == "dallas_arboretum_bulk" and url == "bulk:dallas_arboretum":
            # Dallas Arboretum sync
            from extractors.dallas_arboretum import extract_dallas_arboretum_events
            events = extract_dallas_arboretum_events()
        # Try different extraction methods based on source type
        elif source_type == "ics":
            events = extract_ics(url)
        elif source_type == "rss":
            events = extract_rss(url)
        elif source_type == "eventbrite" or "eventbrite.com" in url:
            # Use Eventbrite API
            events = extract_eventbrite_events(url)
        else:
            # Try JSON-LD first, then HTML fallback
            events = extract_json_ld(url)
            if not events:
                events = extract_html_fallback(url)
        
        if events:
            # Save events to database
            from models.event import Event
            import hashlib
            
            # Map bulk task types to event source types
            event_source_type = source_type
            if source_type == "eventbrite_bulk":
                event_source_type = "eventbrite"
            elif source_type == "dallas_arboretum_bulk":
                event_source_type = "dallas_arboretum"
            
            saved_count = 0
            for event_data in events:
                # Process external images - upload to Supabase Storage
                event_data = process_event_image(event_data)
                
                # Generate unique hash
                hash_string = f"{event_data['title']}{event_data['start_at']}{url}"
                fid_hash = hashlib.md5(hash_string.encode()).hexdigest()
                
                # Check if event already exists
                existing = db.query(Event).filter(Event.fid_hash == fid_hash).first()
                if not existing:
                    event = Event(
                        title=event_data["title"],
                        description=event_data.get("description"),
                        start_at=event_data["start_at"],
                        end_at=event_data.get("end_at"),
                        venue=event_data.get("venue"),
                        address=event_data.get("address"),
                        city=event_data.get("city"),
                        price_tier=event_data.get("price_tier", "free"),
                        price_amount=event_data.get("price_amount"),
                        image_url=event_data.get("image_url"),
                        source_url=event_data.get("source_url", url),
                        source_type=event_source_type,
                        category=event_data.get("category"),
                        fid_hash=fid_hash,
                        status="DRAFT"  # Save as DRAFT first, user can publish from CMS
                    )
                    db.add(event)
                    saved_count += 1
            
            db.commit()
            
            update_task_status(
                db, task_id, "done",
                logs=f"Successfully extracted {len(events)} events, saved {saved_count} new events",
                events_extracted=saved_count
            )
            print(f"✓ Task {task_id} completed: {saved_count} events saved")
        else:
            update_task_status(
                db, task_id, "failed",
                error_message="No event data found"
            )
            print(f"✗ Task {task_id} failed: No events found")
    
    except Exception as e:
        error_msg = str(e)
        update_task_status(
            db, task_id, "failed",
            error_message=error_msg
        )
        print(f"✗ Task {task_id} failed: {error_msg}")
    
    finally:
        db.close()

def main():
    """Main worker loop"""
    print("Worker started. Waiting for tasks...")
    
    while True:
        try:
            task = get_next_task()
            if task:
                process_task(task)
            else:
                # No tasks, wait a bit
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nWorker stopped")
            break
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

"""
Script to delete past events from the database
Run this once to clean up any outdated events
"""
import os
import sys
from datetime import datetime, timezone

# Add worker directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from database import get_db
from models.event import Event

def cleanup_past_events():
    db = next(get_db())
    
    # Get current time
    now = datetime.now(timezone.utc)
    
    # Count past events
    past_events = db.query(Event).filter(Event.start_at < now).all()
    count = len(past_events)
    
    if count == 0:
        print("✅ No past events found. Database is clean!")
        return
    
    print(f"📊 Found {count} past events to delete:\n")
    
    # Show sample
    for event in past_events[:5]:
        print(f"   - {event.title} (Date: {event.start_at.date()})")
    
    if count > 5:
        print(f"   ... and {count - 5} more\n")
    
    # Confirm deletion
    response = input(f"\n⚠️  Delete all {count} past events? (yes/no): ")
    
    if response.lower() == 'yes':
        # Delete past events
        deleted = db.query(Event).filter(Event.start_at < now).delete()
        db.commit()
        print(f"\n✅ Successfully deleted {deleted} past events!")
        print("🎉 Database now contains only upcoming events")
    else:
        print("\n❌ Cleanup cancelled")

if __name__ == "__main__":
    cleanup_past_events()

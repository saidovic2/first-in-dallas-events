"""
Delete all Dallas Library events from the database
"""
import os
import sys

# Add worker directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from database import get_db
from models.event import Event

def delete_dallas_library_events():
    db = next(get_db())
    
    try:
        # Count Dallas Library events
        dallas_events = db.query(Event).filter(Event.source_type == 'DALLAS_LIBRARY').all()
        count = len(dallas_events)
        
        if count == 0:
            print("✅ No Dallas Library events found in database")
            return
        
        print(f"📊 Found {count} Dallas Library events:\n")
        
        # Show sample
        for event in dallas_events[:5]:
            print(f"   - {event.title} (Date: {event.start_at.date()})")
        
        if count > 5:
            print(f"   ... and {count - 5} more\n")
        
        # Delete all Dallas Library events
        deleted = db.query(Event).filter(Event.source_type == 'DALLAS_LIBRARY').delete()
        db.commit()
        
        print(f"\n✅ Successfully deleted {deleted} Dallas Library events!")
        print("🎉 Database is clean - ready for fresh sync")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🗑️  Delete Dallas Library Events")
    print("="*80 + "\n")
    
    delete_dallas_library_events()

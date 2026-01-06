"""
Delete all Facebook events from the database
Facebook events are often low-quality, so cleaning them up before bulk sync
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.event import Event
from config import settings
from datetime import datetime, timezone

def delete_facebook_events():
    """Delete all events from Facebook source"""
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("🗑️  Facebook Events Deletion")
    print("=" * 60)
    
    try:
        # Find all Facebook events
        facebook_events = db.query(Event).filter(
            Event.source_type.ilike('%facebook%')
        ).all()
        
        if not facebook_events:
            print("✅ No Facebook events found in database")
            return
        
        total_count = len(facebook_events)
        
        # Count by status
        published_count = sum(1 for e in facebook_events if e.status == 'PUBLISHED')
        draft_count = sum(1 for e in facebook_events if e.status == 'DRAFT')
        
        # Count upcoming vs past
        now = datetime.now(timezone.utc)
        upcoming_count = sum(1 for e in facebook_events if e.start_at > now)
        past_count = sum(1 for e in facebook_events if e.start_at <= now)
        
        print(f"\n📊 Found {total_count} Facebook events:")
        print(f"   - Published: {published_count}")
        print(f"   - Draft: {draft_count}")
        print(f"   - Upcoming: {upcoming_count}")
        print(f"   - Past: {past_count}")
        print()
        
        # Show samples
        print("Sample Facebook events to be deleted:")
        for event in facebook_events[:10]:
            status_icon = "✅" if event.status == "PUBLISHED" else "📝"
            date_str = event.start_at.strftime('%Y-%m-%d')
            print(f"   {status_icon} {event.title[:50]}... ({date_str})")
        
        if total_count > 10:
            print(f"   ... and {total_count - 10} more")
        
        print()
        print("⚠️  WARNING: This action cannot be undone!")
        print("=" * 60)
        
        # Confirmation
        response = input(f"\nDelete all {total_count} Facebook events? Type 'DELETE' to confirm: ")
        
        if response != 'DELETE':
            print("\n❌ Deletion cancelled")
            return
        
        print("\n🗑️  Deleting Facebook events...")
        
        # Delete all Facebook events
        deleted_count = db.query(Event).filter(
            Event.source_type.ilike('%facebook%')
        ).delete(synchronize_session=False)
        
        db.commit()
        
        print(f"\n✅ Successfully deleted {deleted_count} Facebook events!")
        print()
        
        # Show remaining events
        remaining_events = db.query(Event).count()
        upcoming_remaining = db.query(Event).filter(Event.start_at > now).count()
        
        print("📊 Database Summary After Deletion:")
        print(f"   Total events: {remaining_events}")
        print(f"   Upcoming events: {upcoming_remaining}")
        print()
        print("🎉 Database cleaned! Ready for bulk sync.")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    delete_facebook_events()

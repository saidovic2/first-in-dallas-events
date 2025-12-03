"""
Check if draft events are in the database
"""
import os
import sys

# Add worker directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from database import get_db
from models.event import Event
from datetime import datetime, timezone

def check_draft_events():
    db = next(get_db())
    
    try:
        # Get all draft events
        draft_events = db.query(Event).filter(Event.status == 'DRAFT').all()
        
        print(f"\n{'='*80}")
        print(f"📊 DRAFT EVENTS CHECK")
        print(f"{'='*80}\n")
        
        print(f"Total DRAFT events: {len(draft_events)}\n")
        
        if draft_events:
            # Group by source
            by_source = {}
            for event in draft_events:
                source = event.source_type or 'Unknown'
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(event)
            
            print("Breakdown by source:")
            for source, events in sorted(by_source.items()):
                print(f"  📌 {source}: {len(events)} events")
            
            print(f"\n{'='*80}")
            print("Sample of recent DRAFT events:")
            print(f"{'='*80}\n")
            
            # Show 10 most recent
            recent = sorted(draft_events, key=lambda e: e.created_at, reverse=True)[:10]
            for i, event in enumerate(recent, 1):
                now = datetime.now(timezone.utc)
                is_past = event.start_at < now if event.start_at.tzinfo else event.start_at.replace(tzinfo=timezone.utc) < now
                past_marker = "⚠️ PAST" if is_past else "✓ FUTURE"
                
                print(f"{i}. [{past_marker}] {event.title}")
                print(f"   Source: {event.source_type}")
                print(f"   Date: {event.start_at}")
                print(f"   Created: {event.created_at}")
                print(f"   Image: {'✓ Yes' if event.image_url else '✗ No'}")
                print()
        else:
            print("❌ No DRAFT events found in database!")
            
            # Check total events
            total = db.query(Event).count()
            published = db.query(Event).filter(Event.status == 'PUBLISHED').count()
            print(f"\nTotal events in database: {total}")
            print(f"  - PUBLISHED: {published}")
            print(f"  - DRAFT: 0")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_draft_events()

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from database import get_db
from models.event import Event

db = next(get_db())

# Count all Dallas Library events
total = db.query(Event).filter(Event.source_type == 'DALLAS_LIBRARY').count()
print(f"✅ Total Dallas Library events in DB: {total}")

# Count draft events
draft = db.query(Event).filter(
    Event.source_type == 'DALLAS_LIBRARY',
    Event.status == 'DRAFT'
).count()
print(f"📝 Draft Dallas Library events: {draft}")

# Count published events
published = db.query(Event).filter(
    Event.source_type == 'DALLAS_LIBRARY',
    Event.status == 'PUBLISHED'
).count()
print(f"📢 Published Dallas Library events: {published}")

# Check images
events_with_images = db.query(Event).filter(
    Event.source_type == 'DALLAS_LIBRARY',
    Event.image_url.isnot(None),
    Event.image_url != ''
).count()
print(f"🖼️  Events with images: {events_with_images}")

events_no_images = db.query(Event).filter(
    Event.source_type == 'DALLAS_LIBRARY',
    Event.image_url.is_(None)
).count()
print(f"❌ Events without images: {events_no_images}")

# Sample event to check image
sample = db.query(Event).filter(
    Event.source_type == 'DALLAS_LIBRARY'
).first()

if sample:
    print(f"\n📋 Sample event:")
    print(f"   Title: {sample.title}")
    print(f"   Status: {sample.status}")
    print(f"   Image URL: {sample.image_url}")
    print(f"   Source URL: {sample.source_url}")

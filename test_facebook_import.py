"""Test a single Facebook event import"""
import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'api'))

from database import get_db
from models.event import Event
from datetime import datetime
import hashlib

# Test creating a simple Facebook event
test_event_data = {
    'title': 'Test Facebook Event',
    'source_url': 'https://facebook.com/test',
    'venue': 'Test Venue',
    'address': 'Dallas, TX',
    'city': 'Dallas',
    'start_at': datetime.now(),
    'end_at': None,
    'description': 'Test description',
    'image_url': None,
    'price_tier': 'FREE',
    'category': 'Entertainment',
    'source_type': 'FACEBOOK',
    'fid_hash': hashlib.sha256(f"test{datetime.now()}".encode()).hexdigest()[:32],
    'status': 'DRAFT'
}

print("🧪 Testing Facebook event creation...")
print(f"Source type: {test_event_data['source_type']}")

try:
    db = next(get_db())
    
    # Try to create the event
    event = Event(**test_event_data)
    print("✅ Event object created successfully")
    
    db.add(event)
    print("✅ Event added to session")
    
    db.flush()
    print(f"✅ Event flushed (ID: {event.id})")
    
    db.commit()
    print("✅ Event committed to database")
    
    # Verify
    check = db.query(Event).filter(Event.id == event.id).first()
    if check:
        print(f"✅ Event verified in database!")
        print(f"   Title: {check.title}")
        print(f"   Source Type: {check.source_type}")
        print(f"   Status: {check.status}")
    
    db.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

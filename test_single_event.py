"""Test importing a single event to see exact error"""
import sys
sys.path.insert(0, 'api')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import hashlib

# Import Event model
from models.event import Event
from database import SessionLocal

# Test data matching Apify structure
test_event = {
    'title': 'Test Event',
    'source_url': 'https://www.ticketmaster.com/test',
    'venue': 'Test Venue',
    'address': '123 Test St, Dallas, TX',
    'city': 'Dallas',
    'start_at': datetime.now(),
    'end_at': None,
    'description': 'Test description',
    'image_url': 'https://example.com/image.jpg',
    'price_tier': 'paid',
    'category': 'Music & Concerts',
    'source_type': 'TICKETMASTER',
    'fid_hash': hashlib.sha256(b'test').hexdigest()[:32],
    'status': 'DRAFT'
}

try:
    db = SessionLocal()
    
    print("Creating event...")
    event = Event(**test_event)
    
    print("Adding to database...")
    db.add(event)
    
    print("Flushing...")
    db.flush()
    
    print(f"[OK] Event created with ID: {event.id}")
    
    db.commit()
    db.close()
    
    print("[OK] Test passed!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

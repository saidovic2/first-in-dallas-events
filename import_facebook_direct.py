"""
Direct import Facebook events to Railway database
Bypasses the Settings class to use Railway DATABASE_URL directly
"""

import os
import requests
from datetime import datetime
import hashlib
from dateutil import parser as date_parser
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Get Railway DATABASE_URL directly
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file!")
    exit(1)

print(f"🔗 Connecting to Railway: {DATABASE_URL[:50]}...")

# Create database connection directly
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Event model (simplified)
class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True))
    venue = Column(String)
    address = Column(String)
    city = Column(String)
    price_tier = Column(String)
    price_amount = Column(Numeric(10, 2))
    image_url = Column(String)
    source_url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    category = Column(String)
    fid_hash = Column(String, unique=True, nullable=False)
    status = Column(String, default="DRAFT", nullable=False)
    wp_post_id = Column(Integer)
    is_featured = Column(Boolean, default=False)
    featured_tier = Column(String(20))
    featured_until = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))

# Configuration
APIFY_API_TOKEN = "apify_api_SyxGrvd54Tx0gfbRlbqfIK823e4Bf11UutCW"
DATASET_ID = "eYGPqTQvvEtOsB4Nm"


def fetch_apify_dataset(dataset_id, api_token):
    """Fetch dataset items"""
    print(f"\n{'='*80}")
    print(f"📘 FETCHING FACEBOOK EVENTS FROM APIFY")
    print(f"{'='*80}\n")
    
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={api_token}"
    
    try:
        response = requests.get(dataset_url, timeout=60)
        response.raise_for_status()
        events = response.json()
        print(f"✓ Found {len(events)} Facebook events!\n")
        return events
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def categorize_event(name, description, categories):
    """Categorize event"""
    text = f"{name} {description}".lower()
    
    if categories:
        for cat in categories:
            label = cat.get('label', '').lower()
            if 'music' in label or 'concert' in label:
                return 'Music & Concerts'
            elif 'sport' in label:
                return 'Sports & Recreation'
            elif 'art' in label or 'theatre' in label:
                return 'Arts & Culture'
            elif 'food' in label or 'dining' in label:
                return 'Food & Dining'
            elif 'game' in label:
                return 'Entertainment'
            elif 'family' in label or 'kid' in label:
                return 'Family & Kids'
    
    if any(word in text for word in ['concert', 'music', 'band', 'singer']):
        return 'Music & Concerts'
    elif any(word in text for word in ['sport', 'football', 'basketball', 'baseball']):
        return 'Sports & Recreation'
    elif any(word in text for word in ['art', 'museum', 'gallery', 'theatre', 'theater']):
        return 'Arts & Culture'
    elif any(word in text for word in ['food', 'dining', 'restaurant', 'wine']):
        return 'Food & Dining'
    elif any(word in text for word in ['kid', 'child', 'family']):
        return 'Family & Kids'
    else:
        return 'Entertainment'


def transform_event(apify_event):
    """Transform event"""
    if apify_event.get('isPast', False):
        return None
    if apify_event.get('isOnline', False) and not apify_event.get('location'):
        return None
    
    title = apify_event.get('name', 'Untitled Event')
    url = apify_event.get('url', '')
    description = apify_event.get('description', '')
    
    # Parse date
    start_at = None
    utc_start = apify_event.get('utcStartDate')
    if utc_start:
        try:
            start_at = date_parser.parse(utc_start)
        except:
            pass
    
    if not start_at:
        start_at = datetime.now()
    
    # Location
    location = apify_event.get('location', {})
    venue = location.get('name', 'Unknown Venue')
    city = location.get('city')
    if not city:
        contextual = location.get('contextualName', '')
        if ',' in contextual:
            city = contextual.split(',')[0].strip()
    if not city:
        city = 'Dallas'
    
    address = location.get('streetAddress', '')
    if not address:
        address = venue if venue != 'Unknown Venue' else f"{city}, TX"
    
    image_url = apify_event.get('imageUrl', '')
    
    # Price
    tickets_info = apify_event.get('ticketsInfo', {})
    ticket_title = tickets_info.get('title', '').lower() if tickets_info else ''
    price_tier = 'FREE' if 'free' in ticket_title or not tickets_info.get('buyUrl') else 'PAID'
    
    # Category
    categories = apify_event.get('discoveryCategories', [])
    category = categorize_event(title, description, categories)
    
    # Hash
    fid_hash = hashlib.sha256(f"{url}{title}{start_at}".encode()).hexdigest()[:32]
    
    return {
        'title': title[:200],
        'source_url': url,
        'venue': venue[:150] if venue else 'Unknown Venue',
        'address': address[:300] if address else f"{city}, TX",
        'city': city,
        'start_at': start_at,
        'end_at': None,
        'description': description[:1000] if description else None,
        'image_url': image_url if image_url else None,
        'price_tier': price_tier,
        'category': category,
        'source_type': 'FACEBOOK',
        'fid_hash': fid_hash,
        'status': 'DRAFT',
        'created_at': datetime.now()
    }


def import_events(events):
    """Import events to Railway"""
    print(f"{'='*80}")
    print(f"💾 IMPORTING TO RAILWAY DATABASE")
    print(f"{'='*80}\n")
    
    db = SessionLocal()
    imported = 0
    duplicates = 0
    skipped = 0
    errors = 0
    
    try:
        for i, apify_event in enumerate(events, 1):
            try:
                event_name = apify_event.get('name', 'Untitled')[:50]
                print(f"[{i}/{len(events)}] {event_name}...", end=" ")
                
                event_data = transform_event(apify_event)
                
                if event_data is None:
                    print("⏭️  Skipped")
                    skipped += 1
                    continue
                
                # Check duplicate
                existing = db.query(Event).filter(Event.fid_hash == event_data['fid_hash']).first()
                if existing:
                    print("⏭️  Duplicate")
                    duplicates += 1
                    continue
                
                # Create event
                event = Event(**event_data)
                db.add(event)
                db.flush()
                
                print(f"✅ ID: {event.id}")
                imported += 1
                
            except Exception as e:
                print(f"❌ {str(e)[:40]}")
                errors += 1
                db.rollback()
                continue
        
        # Commit all
        db.commit()
        
        print(f"\n{'='*80}")
        print(f"📊 IMPORT SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Imported: {imported} events")
        print(f"⏭️  Skipped: {skipped} events")
        print(f"⏭️  Duplicates: {duplicates} events")
        print(f"❌ Errors: {errors} events")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Commit error: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    events = fetch_apify_dataset(DATASET_ID, APIFY_API_TOKEN)
    
    if not events:
        print("❌ No events fetched")
        return
    
    print(f"🚀 Importing {len(events)} events to Railway database...\n")
    import_events(events)


if __name__ == "__main__":
    main()

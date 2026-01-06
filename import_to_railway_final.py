"""
FINAL VERSION: Import Facebook events DIRECTLY to Railway
Completely standalone - no imports from api folder
"""

import os
import requests
from datetime import datetime
import hashlib
from dateutil import parser as date_parser
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Numeric, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

print("="*80)
print("FACEBOOK EVENTS IMPORT TO RAILWAY")
print("="*80)

# Load .env FIRST
load_dotenv()

# Get Railway DATABASE_URL
RAILWAY_URL = os.getenv('DATABASE_URL')

if not RAILWAY_URL or 'localhost' in RAILWAY_URL:
    print(f"❌ ERROR: DATABASE_URL not set correctly!")
    print(f"   Current: {RAILWAY_URL}")
    print(f"   Expected: Railway PostgreSQL URL")
    exit(1)

print(f"\n✅ Connecting to Railway:")
print(f"   {RAILWAY_URL[:70]}...")

# Create engine with Railway URL
engine = create_engine(RAILWAY_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Event model
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))

# Apify config
APIFY_TOKEN = "apify_api_SyxGrvd54Tx0gfbRlbqfIK823e4Bf11UutCW"
DATASET_ID = "eYGPqTQvvEtOsB4Nm"


def fetch_events():
    """Fetch from Apify"""
    print(f"\n📥 Fetching from Apify dataset {DATASET_ID}...")
    url = f"https://api.apify.com/v2/datasets/{DATASET_ID}/items?token={APIFY_TOKEN}"
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        events = response.json()
        print(f"✅ Found {len(events)} events\n")
        return events
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def categorize(name, desc, cats):
    """Simple categorization"""
    text = f"{name or ''} {desc or ''}".lower()
    
    if cats:
        for c in cats:
            label = (c.get('label') or '').lower()
            if 'music' in label: return 'Music & Concerts'
            if 'sport' in label: return 'Sports & Recreation'
            if 'art' in label or 'theatre' in label: return 'Arts & Culture'
    
    if any(w in text for w in ['concert', 'music', 'band']):
        return 'Music & Concerts'
    if any(w in text for w in ['sport', 'game', 'football']):
        return 'Sports & Recreation'
    if any(w in text for w in ['art', 'museum', 'theatre']):
        return 'Arts & Culture'
    if any(w in text for w in ['food', 'dining', 'restaurant']):
        return 'Food & Dining'
    if any(w in text for w in ['kid', 'family', 'child']):
        return 'Family & Kids'
    
    return 'Entertainment'


def transform(event):
    """Transform event"""
    # Skip past/online
    if event.get('isPast'): return None
    if event.get('isOnline') and not event.get('location'): return None
    
    title = (event.get('name') or 'Untitled')[:200]
    url = event.get('url', '')
    desc = (event.get('description') or '')[:1000]
    
    # Date
    start_at = None
    if event.get('utcStartDate'):
        try:
            start_at = date_parser.parse(event['utcStartDate'])
        except:
            pass
    if not start_at:
        start_at = datetime.now()
    
    # Location
    loc = event.get('location') or {}
    venue = (loc.get('name') or 'Unknown Venue')[:150]
    city = loc.get('city') or 'Dallas'
    if not city and loc.get('contextualName'):
        city = loc['contextualName'].split(',')[0].strip()
    
    address = (loc.get('streetAddress') or venue)[:300]
    
    image = event.get('imageUrl')
    
    # Price
    tickets = event.get('ticketsInfo') or {}
    ticket_title = (tickets.get('title') or '').lower()
    price = 'FREE' if ('free' in ticket_title or not tickets.get('buyUrl')) else 'PAID'
    
    # Category
    category = categorize(title, desc, event.get('discoveryCategories', []))
    
    # Hash
    fid_hash = hashlib.sha256(f"{url}{title}{start_at}".encode()).hexdigest()[:32]
    
    return {
        'title': title,
        'source_url': url,
        'venue': venue,
        'address': address,
        'city': city,
        'start_at': start_at,
        'description': desc or None,
        'image_url': image,
        'price_tier': price,
        'category': category,
        'source_type': 'FACEBOOK',
        'fid_hash': fid_hash,
        'status': 'DRAFT'
    }


def import_to_railway(events):
    """Import to Railway"""
    print(f"{'='*80}")
    print(f"💾 IMPORTING TO RAILWAY DATABASE")
    print(f"{'='*80}\n")
    
    session = SessionLocal()
    imported = 0
    skipped = 0
    duplicates = 0
    errors = 0
    
    try:
        for i, evt in enumerate(events, 1):
            try:
                name = (evt.get('name') or 'Untitled')[:40]
                print(f"[{i}/{len(events)}] {name}... ", end="")
                
                data = transform(evt)
                if not data:
                    print("⏭️  Skipped")
                    skipped += 1
                    continue
                
                # Check duplicate
                exists = session.query(Event).filter(Event.fid_hash == data['fid_hash']).first()
                if exists:
                    print("⏭️  Duplicate")
                    duplicates += 1
                    continue
                
                # Create
                event = Event(**data)
                session.add(event)
                session.flush()
                
                print(f"✅ ID: {event.id}")
                imported += 1
                
                # Commit every 10 events
                if imported % 10 == 0:
                    session.commit()
                    print(f"   💾 Committed {imported} events so far...")
                
            except Exception as e:
                print(f"❌ {str(e)[:50]}")
                errors += 1
                session.rollback()
        
        # Final commit
        session.commit()
        print(f"\n{'='*80}")
        print(f"✅ SUCCESSFULLY COMMITTED TO RAILWAY!")
        print(f"{'='*80}")
        print(f"✅ Imported: {imported}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"⏭️  Duplicates: {duplicates}")
        print(f"❌ Errors: {errors}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        session.rollback()
    finally:
        session.close()


def main():
    events = fetch_events()
    if not events:
        return
    
    print(f"🚀 Starting import of {len(events)} events...\n")
    import_to_railway(events)
    
    print("\n✅ Import complete! Check your Railway database.")


if __name__ == "__main__":
    main()

"""
Simple Apify Ticketmaster Import Script
No config dependencies - works standalone
"""

import os
import sys
import requests
from datetime import datetime
import hashlib
from dateutil import parser as date_parser
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Numeric, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Configuration
APIFY_API_TOKEN = "apify_api_SyxGrvd54Tx0gfbRlbqfIK823e4Bf11UutCW"
DATASET_ID = "MFCwnLRBHTdcsJKpS"  # UPDATE THIS with your new dataset ID
TICKETMASTER_AFFILIATE_ID = "6497023"

# Database URL - Railway public connection
DATABASE_URL = 'postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway'

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
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


def add_affiliate_tracking(url, affiliate_id):
    """Add Ticketmaster affiliate tracking"""
    if not url or not affiliate_id:
        return url
    
    separator = '&' if '?' in url else '?'
    affiliate_param = f"CAMEFROM=CMPAFFILIATE_{affiliate_id}"
    
    if 'CAMEFROM' not in url:
        url = f"{url}{separator}{affiliate_param}"
    
    return url


def fetch_apify_dataset(dataset_id, api_token):
    """Fetch dataset from Apify"""
    print(f"\n{'='*80}")
    print(f"FETCHING TICKETMASTER EVENTS FROM APIFY")
    print(f"{'='*80}\n")
    
    print(f"Fetching dataset: {dataset_id}...")
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={api_token}"
    
    try:
        response = requests.get(dataset_url, timeout=60)
        response.raise_for_status()
        events = response.json()
        
        print(f"   ✓ Found {len(events)} Ticketmaster events!")
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error fetching dataset: {e}")
        return None


def transform_apify_event(apify_event):
    """Transform Apify event to CMS schema"""
    
    title = apify_event.get('name', 'Untitled Event')
    url = apify_event.get('url', '')
    description = apify_event.get('description', '')
    
    # Add affiliate tracking
    url = add_affiliate_tracking(url, TICKETMASTER_AFFILIATE_ID)
    
    # Skip parking/valet/misc items
    segment = apify_event.get('segmentName', '')
    if segment in ['Miscellaneous', 'Undefined']:
        if any(skip in title.lower() for skip in ['parking', 'valet', 'pre-show pass', 'happy camper pass']):
            return None
    
    # Parse date
    date_title = apify_event.get('dateTitle', '')
    current_year = datetime.now().year
    
    try:
        if '-' not in date_title or 'Dec' not in date_title.split('-')[1]:
            date_str = f"{date_title} {current_year}"
            start_at = date_parser.parse(date_str)
        else:
            first_date = date_title.split('-')[0].strip()
            date_str = f"{first_date} {current_year}"
            start_at = date_parser.parse(date_str)
        
        if start_at < datetime.now():
            start_at = start_at.replace(year=current_year + 1)
    except:
        start_at = datetime.now()
    
    # Extract venue from description
    venue = 'Unknown Venue'
    if '|' in description:
        parts = description.split('|')
        if len(parts) >= 3:
            venue_part = parts[2].strip()
            venue = venue_part.split(',')[0].strip()
    
    # Address
    street = apify_event.get('streetAddress', '')
    city = apify_event.get('addressLocality', 'Dallas')
    state = apify_event.get('addressRegion', 'TX')
    address = f"{street}, {city}, {state}".strip(', ')
    
    # Image
    image_url = apify_event.get('image', '')
    
    # Price tier (MUST BE UPPERCASE for database enum)
    price = apify_event.get('offer.price')
    if price and float(price) == 0:
        price_tier = 'FREE'
    else:
        price_tier = 'PAID'  # Default to PAID
    
    # Category
    category_mapping = {
        'Music': 'Music & Concerts',
        'Sports': 'Sports & Recreation',
        'Arts & Theatre': 'Arts & Culture',
        'Theatre': 'Arts & Culture',
        'Film': 'Arts & Culture',
        'Family': 'Family & Kids',
    }
    category = category_mapping.get(segment, 'Entertainment')
    
    # Hash
    fid_hash = hashlib.sha256(f"{url}{title}{start_at}".encode()).hexdigest()[:32]
    
    return {
        'title': title[:200],
        'source_url': url,
        'venue': venue[:150],
        'address': address[:300],
        'city': city,
        'start_at': start_at,
        'end_at': None,
        'description': description[:1000] if description else None,
        'image_url': image_url,
        'price_tier': price_tier,
        'category': category,
        'source_type': 'TICKETMASTER',
        'fid_hash': fid_hash,
        'status': 'DRAFT'
    }


def import_events_to_cms(events):
    """Import events to database"""
    
    print(f"\n{'='*80}")
    print(f"IMPORTING EVENTS TO CMS")
    print(f"Affiliate tracking enabled (ID: {TICKETMASTER_AFFILIATE_ID})")
    print(f"{'='*80}\n")
    
    db = SessionLocal()
    
    imported = 0
    duplicates = 0
    skipped = 0
    errors = 0
    
    for i, apify_event in enumerate(events, 1):
        try:
            print(f"[{i}/{len(events)}] Processing: {apify_event.get('name', 'Untitled')[:50]}...")
            
            event_data = transform_apify_event(apify_event)
            
            if event_data is None:
                print(f"   >> Skipped (parking/valet/misc)")
                skipped += 1
                continue
            
            existing = db.query(Event).filter(Event.fid_hash == event_data['fid_hash']).first()
            if existing:
                print(f"   >> Skipped (duplicate - already exists as ID {existing.id})")
                duplicates += 1
                continue
            
            event = Event(**event_data)
            db.add(event)
            db.flush()
            
            print(f"   [OK] Imported (ID: {event.id})")
            imported += 1
            
        except Exception as e:
            error_msg = str(e)
            print(f"   [ERROR] {error_msg[:80]}")
            if errors == 0:  # Show full error for first failure
                print(f"\nFull error details:")
                print(f"   {error_msg}")
                print(f"   Event data: {event_data if 'event_data' in locals() else 'N/A'}\n")
            errors += 1
            db.rollback()
            continue
    
    try:
        db.commit()
        print(f"\n{'='*80}")
        print(f"IMPORT SUMMARY")
        print(f"{'='*80}")
        print(f"[OK] Imported: {imported} events")
        print(f"[>>] Skipped (parking/valet): {skipped} events")
        print(f"[>>] Skipped (duplicates): {duplicates} events")
        print(f"[ERROR] Errors: {errors} events")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"\n[ERROR] Error committing to database: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function"""
    
    events = fetch_apify_dataset(DATASET_ID, APIFY_API_TOKEN)
    
    if not events:
        print("\n[ERROR] No events fetched.\n")
        return
    
    if events:
        print(f"\nSample Event:")
        print(f"   Title: {events[0].get('name', 'N/A')}")
        print(f"   Segment: {events[0].get('segmentName', 'N/A')}")
        print(f"   Date: {events[0].get('dateTitle', 'N/A')} {events[0].get('dateSubTitle', '')}")
        print(f"   Location: {events[0].get('addressLocality', 'N/A')}, {events[0].get('addressRegion', 'N/A')}")
    
    print(f"\n[WARNING] About to import {len(events)} events into your CMS.")
    response = input("   Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n[CANCELLED] Import cancelled.\n")
        return
    
    import_events_to_cms(events)


if __name__ == "__main__":
    main()

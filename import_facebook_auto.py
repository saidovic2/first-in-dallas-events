"""
Auto-import Facebook events from Apify (no confirmation prompt)
Run ID: uFdFpDadtSxmlULdf  
Dataset ID: eYGPqTQvvEtOsB4Nm
"""

import os
import sys
import requests
from datetime import datetime
import hashlib
from dateutil import parser as date_parser
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Verify Railway DATABASE_URL is loaded
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"🔗 Using database: {DATABASE_URL[:30]}...")

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from database import get_db
from models.event import Event

# ========================================
# CONFIGURATION
# ========================================
APIFY_API_TOKEN = "apify_api_SyxGrvd54Tx0gfbRlbqfIK823e4Bf11UutCW"
DATASET_ID = "eYGPqTQvvEtOsB4Nm"
RUN_ID = "uFdFpDadtSxmlULdf"


def fetch_apify_dataset(dataset_id, api_token):
    """Fetch dataset items directly from dataset ID"""
    
    print(f"\n{'='*80}")
    print(f"📘 FETCHING FACEBOOK EVENTS FROM APIFY")
    print(f"{'='*80}\n")
    
    print(f"📥 Fetching dataset: {dataset_id}...")
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={api_token}"
    
    try:
        response = requests.get(dataset_url, timeout=60)
        response.raise_for_status()
        events = response.json()
        
        print(f"   ✓ Found {len(events)} Facebook events!")
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error fetching dataset: {e}")
        return None


def categorize_event(name, description, categories):
    """Categorize event based on name, description, and discovery categories"""
    text = f"{name} {description}".lower()
    
    # Check discovery categories first
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
    
    # Fallback to text analysis
    if any(word in text for word in ['concert', 'music', 'band', 'singer', 'live music', 'dj']):
        return 'Music & Concerts'
    elif any(word in text for word in ['game', 'sport', 'football', 'basketball', 'baseball', 'soccer']):
        return 'Sports & Recreation'
    elif any(word in text for word in ['art', 'museum', 'gallery', 'theatre', 'theater', 'play', 'exhibition']):
        return 'Arts & Culture'
    elif any(word in text for word in ['food', 'dining', 'restaurant', 'wine', 'beer', 'tasting', 'brunch']):
        return 'Food & Dining'
    elif any(word in text for word in ['kid', 'child', 'family', 'children']):
        return 'Family & Kids'
    elif any(word in text for word in ['business', 'networking', 'professional', 'conference', 'seminar']):
        return 'Business & Networking'
    elif any(word in text for word in ['market', 'fair', 'festival', 'bazaar']):
        return 'Markets & Fairs'
    else:
        return 'Entertainment'


def transform_apify_event(apify_event):
    """Transform Apify Facebook event to CMS schema"""
    
    # Skip past events
    if apify_event.get('isPast', False):
        return None
    
    # Skip online-only events
    if apify_event.get('isOnline', False) and not apify_event.get('location'):
        return None
    
    # Extract basic fields
    title = apify_event.get('name', 'Untitled Event')
    url = apify_event.get('url', '')
    description = apify_event.get('description', '')
    
    # Date parsing
    start_at = None
    utc_start = apify_event.get('utcStartDate')
    if utc_start:
        try:
            start_at = date_parser.parse(utc_start)
        except:
            pass
    
    if not start_at:
        date_sentence = apify_event.get('dateTimeSentence', '')
        if date_sentence:
            try:
                start_at = date_parser.parse(date_sentence)
            except:
                start_at = datetime.now()
        else:
            start_at = datetime.now()
    
    # Location
    location = apify_event.get('location', {})
    venue = location.get('name', 'Unknown Venue')
    
    # Try to extract city
    city = location.get('city')
    if not city:
        contextual = location.get('contextualName', '')
        if contextual:
            parts = contextual.split(',')
            if len(parts) >= 1:
                city = parts[0].strip()
    
    if not city:
        city = 'Dallas'
    
    # Address
    street = location.get('streetAddress', '')
    address = apify_event.get('address', street)
    
    if not address and venue and venue != 'Unknown Venue':
        address = venue
    
    if not address:
        address = f"{city}, TX"
    
    # Image
    image_url = apify_event.get('imageUrl', '')
    
    # Price tier
    tickets_info = apify_event.get('ticketsInfo', {})
    ticket_title = tickets_info.get('title', '').lower() if tickets_info else ''
    
    if 'free' in ticket_title or not tickets_info.get('buyUrl'):
        price_tier = 'FREE'
    else:
        price_tier = 'PAID'
    
    # Category
    categories = apify_event.get('discoveryCategories', [])
    category = categorize_event(title, description, categories)
    
    # Generate unique hash
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
        'status': 'DRAFT'
    }


def import_events_to_cms(events):
    """Import Apify Facebook events into CMS database"""
    
    print(f"\n{'='*80}")
    print(f"💾 IMPORTING EVENTS TO RAILWAY DATABASE")
    print(f"{'='*80}\n")
    
    db = next(get_db())
    
    imported = 0
    duplicates = 0
    skipped = 0
    errors = 0
    
    for i, apify_event in enumerate(events, 1):
        try:
            event_name = apify_event.get('name', 'Untitled')[:50]
            print(f"[{i}/{len(events)}] Processing: {event_name}...")
            
            # Transform to CMS schema
            event_data = transform_apify_event(apify_event)
            
            # Skip if None (past events, online-only, etc)
            if event_data is None:
                print(f"   ⏭️  Skipped (past/online-only)")
                skipped += 1
                continue
            
            # Check for duplicate
            existing = db.query(Event).filter(Event.fid_hash == event_data['fid_hash']).first()
            if existing:
                print(f"   ⏭️  Skipped (duplicate)")
                duplicates += 1
                continue
            
            # Create event
            event = Event(**event_data)
            db.add(event)
            db.flush()
            
            print(f"   ✅ Imported (ID: {event.id})")
            imported += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:60]}")
            errors += 1
            db.rollback()
            continue
    
    # Commit all
    try:
        db.commit()
        print(f"\n{'='*80}")
        print(f"📊 IMPORT SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Imported: {imported} events")
        print(f"⏭️  Skipped (past/online): {skipped} events")
        print(f"⏭️  Skipped (duplicates): {duplicates} events")
        print(f"❌ Errors: {errors} events")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"\n❌ Error committing to database: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main function"""
    
    # Fetch events from Apify dataset
    events = fetch_apify_dataset(DATASET_ID, APIFY_API_TOKEN)
    
    if not events:
        print("\n❌ No events fetched. Please check your API token and Dataset ID.\n")
        return
    
    # Show sample event
    if events:
        sample = events[0]
        print(f"\n📋 Sample Event:")
        print(f"   Title: {sample.get('name', 'N/A')}")
        print(f"   Date: {sample.get('dateTimeSentence', 'N/A')}")
        location = sample.get('location', {})
        print(f"   Location: {location.get('name', 'N/A')}")
        print(f"   City: {location.get('contextualName', 'N/A')}")
    
    # Auto-import without confirmation
    print(f"\n🚀 Auto-importing {len(events)} Facebook events to Railway database...")
    import_events_to_cms(events)


if __name__ == "__main__":
    main()

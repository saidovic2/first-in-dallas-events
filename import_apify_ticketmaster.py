"""
Import Ticketmaster events from Apify dataset into CMS
Run ID: fXsYxCobNwMDD7E6q
"""

import os
import sys
import requests
from datetime import datetime
import hashlib

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))

from database import get_db
from models.event import Event

# ========================================
# CONFIGURATION
# ========================================
APIFY_API_TOKEN = "apify_api_SyxGrvd54Tx0gfbRlbqfIK823e4Bf11UutCW"
DATASET_ID = "MFCwnLRBHTdcsJKpS"
RUN_ID = "fXsYxCobNwMDD7E6q"  # Optional - we'll use dataset ID directly
TICKETMASTER_AFFILIATE_ID = "6497023"  # Your Impact affiliate ID for commission tracking

def add_affiliate_tracking(url, affiliate_id):
    """
    Add Ticketmaster affiliate tracking to URL for commission earnings
    Format: ?CAMEFROM=CMPAFFILIATE_{affiliate_id} or &CAMEFROM=...
    """
    if not url or not affiliate_id:
        return url
    
    # Check if URL already has query parameters
    separator = '&' if '?' in url else '?'
    
    # Add affiliate tracking parameter
    affiliate_param = f"CAMEFROM=CMPAFFILIATE_{affiliate_id}"
    
    # Only add if not already present
    if 'CAMEFROM' not in url:
        url = f"{url}{separator}{affiliate_param}"
    
    return url


def fetch_apify_dataset(dataset_id, api_token):
    """
    Fetch dataset items directly from dataset ID
    This is faster when you already have the dataset ID
    """
    
    print(f"\n{'='*80}")
    print(f"🎫 FETCHING TICKETMASTER EVENTS FROM APIFY")
    print(f"{'='*80}\n")
    
    print(f"📥 Fetching dataset: {dataset_id}...")
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={api_token}"
    
    try:
        response = requests.get(dataset_url, timeout=60)
        response.raise_for_status()
        events = response.json()
        
        print(f"   ✓ Found {len(events)} Ticketmaster events!")
        return events
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error fetching dataset: {e}")
        print(f"   URL: {dataset_url.split('?')[0]}...")
        return None


def transform_apify_event(apify_event):
    """
    Transform Apify Ticketmaster event to CMS schema
    Apify's structure is simpler than raw Ticketmaster API
    """
    
    # Extract basic fields
    title = apify_event.get('name', 'Untitled Event')
    url = apify_event.get('url', '')
    description = apify_event.get('description', '')
    
    # Add affiliate tracking to URL for commission earnings 💰
    url = add_affiliate_tracking(url, TICKETMASTER_AFFILIATE_ID)
    
    # Skip parking/valet/misc items
    segment = apify_event.get('segmentName', '')
    if segment in ['Miscellaneous', 'Undefined']:
        # Check if it's a parking/valet/pass item
        if any(skip in title.lower() for skip in ['parking', 'valet', 'pre-show pass', 'happy camper pass']):
            return None
    
    # Parse date from dateTitle and dateSubTitle
    # dateTitle examples: "Dec 3", "Oct 27-Dec 8", "Nov 7"
    # dateSubTitle examples: "Wed 7:00pm", "Mon-Mon", "Fri 6:00pm"
    
    date_title = apify_event.get('dateTitle', '')
    date_subtitle = apify_event.get('dateSubTitle', '')
    
    # Extract date - use current year if not specified
    current_year = datetime.now().year
    try:
        # Simple date like "Dec 3"
        if '-' not in date_title or 'Dec' not in date_title.split('-')[1]:
            # Single date
            date_str = f"{date_title} {current_year}"
            start_at = date_parser.parse(date_str)
        else:
            # Date range like "Oct 27-Dec 8" - use first date
            first_date = date_title.split('-')[0].strip()
            date_str = f"{first_date} {current_year}"
            start_at = date_parser.parse(date_str)
        
        # If date is in the past, assume next year
        if start_at < datetime.now():
            start_at = start_at.replace(year=current_year + 1)
            
    except:
        # Fallback to now
        start_at = datetime.now()
    
    # Extract venue from description (format: "Event | Date | Venue, City, State")
    venue = 'Unknown Venue'
    if '|' in description:
        parts = description.split('|')
        if len(parts) >= 3:
            venue_part = parts[2].strip()
            # Split by comma to get venue name
            venue = venue_part.split(',')[0].strip()
    
    # Address
    street = apify_event.get('streetAddress', '')
    city = apify_event.get('addressLocality', 'Dallas')
    state = apify_event.get('addressRegion', 'TX')
    
    address = f"{street}, {city}, {state}".strip(', ')
    
    # Image
    image_url = apify_event.get('image', '')
    
    # Price tier
    price = apify_event.get('offer.price')
    if price and float(price) == 0:
        price_tier = 'FREE'
    elif price and float(price) > 100:
        price_tier = 'PREMIUM'
    else:
        price_tier = 'PAID'  # Default to paid
    
    # Category from segment
    category_mapping = {
        'Music': 'Music & Concerts',
        'Sports': 'Sports & Recreation',
        'Arts & Theatre': 'Arts & Culture',
        'Theatre': 'Arts & Culture',
        'Film': 'Arts & Culture',
        'Family': 'Family & Kids',
    }
    category = category_mapping.get(segment, 'Entertainment')
    
    # Generate unique hash
    fid_hash = hashlib.sha256(f"{url}{title}{start_at}".encode()).hexdigest()[:32]
    
    return {
        'title': title[:200],  # Limit length
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
    """
    Import Apify events into CMS database
    """
    
    print(f"\n{'='*80}")
    print(f"💾 IMPORTING EVENTS TO CMS")
    print(f"💰 Affiliate tracking enabled (ID: {TICKETMASTER_AFFILIATE_ID})")
    print(f"{'='*80}\n")
    
    db = next(get_db())
    
    imported = 0
    duplicates = 0
    skipped = 0
    errors = 0
    
    for i, apify_event in enumerate(events, 1):
        try:
            print(f"[{i}/{len(events)}] Processing: {apify_event.get('name', 'Untitled')[:50]}...")
            
            # Transform to CMS schema
            event_data = transform_apify_event(apify_event)
            
            # Skip if None (parking/valet/etc)
            if event_data is None:
                print(f"   ⏭️  Skipped (parking/valet/misc)")
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
        print(f"⏭️  Skipped (parking/valet): {skipped} events")
        print(f"⏭️  Skipped (duplicates): {duplicates} events")
        print(f"❌ Errors: {errors} events")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"\n❌ Error committing to database: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """
    Main function
    """
    
    # Fetch events from Apify dataset
    events = fetch_apify_dataset(DATASET_ID, APIFY_API_TOKEN)
    
    if not events:
        print("\n❌ No events fetched. Please check your API token and Run ID.\n")
        return
    
    # Show sample event
    if events:
        print(f"\n📋 Sample Event:")
        print(f"   Title: {events[0].get('name', 'N/A')}")
        print(f"   Segment: {events[0].get('segmentName', 'N/A')}")
        print(f"   Date: {events[0].get('dateTitle', 'N/A')} {events[0].get('dateSubTitle', '')}")
        print(f"   Location: {events[0].get('addressLocality', 'N/A')}, {events[0].get('addressRegion', 'N/A')}")
        print(f"   Description: {events[0].get('description', 'N/A')[:80]}...")
    
    # Ask for confirmation
    print(f"\n⚠️  About to import {len(events)} events into your CMS.")
    response = input("   Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Import cancelled.\n")
        return
    
    # Import to CMS
    import_events_to_cms(events)


if __name__ == "__main__":
    main()

"""
Recovery script to fetch Facebook events from previous Apify runs
This avoids re-running Apify actors and incurring additional costs
"""
import os
import sys
import requests
import hashlib
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/events_cms")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

if not APIFY_API_TOKEN:
    print("❌ APIFY_API_TOKEN not set in environment")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Previous Apify Run IDs that already found events
PREVIOUS_RUNS = [
    {"run_id": "0opWQTLgsehwOM0TG", "location": "Dallas, TX"},
    {"run_id": "IodvU5Rx2NfAHU1fK", "location": "Plano, TX"},
    {"run_id": "Vuk9u48uFQ3EItK9Q", "location": "Arlington, TX"},
    {"run_id": "zV9YEogttn5RewQ5k", "location": "Fort Worth, TX"},
]

def fetch_dataset_from_run(run_id, actor_id="apify~facebook-events-scraper"):
    """Fetch dataset from a completed Apify run"""
    try:
        headers = {
            "Authorization": f"Bearer {APIFY_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Get run details to find dataset ID
        status_url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}"
        response = requests.get(status_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        run_data = response.json()
        dataset_id = run_data["data"]["defaultDatasetId"]
        
        print(f"📥 Fetching dataset {dataset_id} from run {run_id}...")
        
        # Fetch dataset items
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        results_response = requests.get(dataset_url, headers=headers, timeout=30)
        results_response.raise_for_status()
        
        return results_response.json()
    
    except Exception as e:
        print(f"❌ Error fetching dataset for run {run_id}: {e}")
        return []

def parse_apify_event(data, location):
    """Parse Apify event data (same logic as worker)"""
    from dateutil import parser as date_parser
    import re
    
    try:
        # Check for errors
        if 'error' in data:
            return None
        
        event = {
            'title': data.get('name') or data.get('title'),
            'description': data.get('description'),
            'start_at': None,
            'end_at': None,
            'venue': None,
            'address': None,
            'city': None,
            'price_tier': 'FREE',
            'price_amount': None,
            'image_url': None,
            'category': None,
            'source_url': None  # Facebook event URL
        }
        
        # Extract Facebook event URL
        event_url = data.get('url') or data.get('link') or data.get('event_url')
        if event_url:
            event['source_url'] = event_url
        elif data.get('id'):
            # Construct URL from event ID
            event['source_url'] = f"https://www.facebook.com/events/{data.get('id')}"
        
        # Parse dates
        start_time = data.get('startTime') or data.get('start_time')
        if start_time:
            try:
                event['start_at'] = date_parser.parse(start_time)
            except:
                pass
        
        end_time = data.get('endTime') or data.get('end_time')
        if end_time:
            try:
                event['end_at'] = date_parser.parse(end_time)
            except:
                pass
        
        # Location
        location_data = data.get('location') or data.get('place')
        if location_data:
            if isinstance(location_data, dict):
                event['venue'] = location_data.get('name')
                event['city'] = location_data.get('city') or location
                event['address'] = location_data.get('street') or location_data.get('address')
            elif isinstance(location_data, str):
                event['venue'] = location_data
                event['city'] = location
        else:
            event['city'] = location
        
        # Image
        photo = (data.get('photo') or data.get('image') or data.get('cover') or 
                 data.get('photoUrl') or data.get('imageUrl') or data.get('coverPhoto'))
        if photo:
            if isinstance(photo, dict):
                event['image_url'] = photo.get('url') or photo.get('source') or photo.get('src')
            elif isinstance(photo, str):
                event['image_url'] = photo
        
        # Pricing
        ticket_url = data.get('ticketUrl') or data.get('ticket_url')
        if ticket_url or (event['description'] and 'ticket' in str(event['description']).lower()):
            event['price_tier'] = 'PAID'
            if event['description']:
                price_match = re.search(r'\$(\d+(?:\.\d{2})?)', event['description'])
                if price_match:
                    try:
                        event['price_amount'] = float(price_match.group(1))
                    except:
                        pass
        
        # Category detection
        category = data.get('category') or data.get('type')
        if category:
            event['category'] = category
        else:
            # Simple category detection
            text = f"{event['title'] or ''} {event['description'] or ''}".lower()
            if any(k in text for k in ['concert', 'music', 'band', 'tour']):
                event['category'] = 'Music'
            elif any(k in text for k in ['comedy', 'stand-up']):
                event['category'] = 'Comedy'
            elif any(k in text for k in ['sports', 'game', 'match']):
                event['category'] = 'Sports'
            else:
                event['category'] = 'Other'
        
        # Validate required fields
        if not event['title'] or not event['start_at']:
            return None
        
        return event
    
    except Exception as e:
        print(f"❌ Error parsing event: {e}")
        return None

def save_events_to_db(events):
    """Save events to database"""
    db = SessionLocal()
    
    try:
        # Import Event model
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
        from models.event import Event
        
        saved_count = 0
        skipped_count = 0
        
        for event_data in events:
            # Use actual Facebook URL or fallback
            source_url = event_data.get('source_url') or "bulk:facebook:dallas"
            
            # Generate hash
            hash_string = f"{event_data['title']}{event_data['start_at']}{source_url}"
            fid_hash = hashlib.md5(hash_string.encode()).hexdigest()
            
            # Check if exists
            existing = db.query(Event).filter(Event.fid_hash == fid_hash).first()
            if existing:
                skipped_count += 1
                continue
            
            # Create event
            event = Event(
                title=event_data["title"],
                description=event_data.get("description"),
                start_at=event_data["start_at"],
                end_at=event_data.get("end_at"),
                venue=event_data.get("venue"),
                address=event_data.get("address"),
                city=event_data.get("city"),
                price_tier=event_data.get("price_tier", "FREE"),
                price_amount=event_data.get("price_amount"),
                image_url=event_data.get("image_url"),
                source_url=source_url,  # Use actual Facebook URL
                source_type="facebook",  # lowercase (now supported in DB)
                category=event_data.get("category"),
                fid_hash=fid_hash,
                status="DRAFT"
            )
            db.add(event)
            saved_count += 1
        
        db.commit()
        print(f"✅ Saved {saved_count} new events, skipped {skipped_count} duplicates")
        return saved_count
        
    except Exception as e:
        print(f"❌ Error saving events: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 0
    finally:
        db.close()

def main():
    """Main recovery process"""
    print("=" * 60)
    print("🔄 Facebook Events Recovery Script")
    print("=" * 60)
    print()
    print("This script recovers events from previous Apify runs")
    print("WITHOUT running new searches (saves money!)")
    print()
    
    all_events = []
    
    for run_info in PREVIOUS_RUNS:
        run_id = run_info["run_id"]
        location = run_info["location"]
        
        print(f"\n📍 Processing {location} (Run ID: {run_id})")
        items = fetch_dataset_from_run(run_id)
        
        if not items:
            print(f"   ⚠️  No data found (dataset may have expired)")
            continue
        
        print(f"   📊 Found {len(items)} items in dataset")
        
        # Parse events
        events_found = 0
        for item in items:
            event = parse_apify_event(item, location)
            if event:
                all_events.append(event)
                events_found += 1
        
        print(f"   ✅ Parsed {events_found} valid events")
    
    print()
    print("=" * 60)
    print(f"🎉 Total events recovered: {len(all_events)}")
    print("=" * 60)
    print()
    
    if all_events:
        print("💾 Saving events to database...")
        saved = save_events_to_db(all_events)
        print()
        print("=" * 60)
        print(f"✅ SUCCESS! {saved} events saved to database")
        print("=" * 60)
        print()
        print("Next steps:")
        print("- Go to http://localhost:3001/events")
        print("- Filter by 'Facebook' source type")
        print("- Review and publish events")
    else:
        print("⚠️  No events could be recovered")
        print("The Apify datasets may have expired (usually 7 days)")
        print("You'll need to run a new sync")

if __name__ == "__main__":
    main()

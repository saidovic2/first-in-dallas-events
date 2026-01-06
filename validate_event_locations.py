"""
Validate Event Location Data Quality
Checks which events have good location data for accurate maps
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.event import Event
from config import settings
from datetime import datetime, timezone

def validate_locations():
    """Analyze location data quality across all events"""
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Get upcoming events only
    now = datetime.now(timezone.utc)
    events = db.query(Event).filter(Event.start_at > now).all()
    
    print(f"📊 Location Data Quality Report")
    print(f"=" * 60)
    print(f"Total upcoming events: {len(events)}\n")
    
    # Categories
    complete_data = []      # Has address + city
    venue_only = []         # Has venue but no address
    missing_location = []   # Missing both
    generic_venues = []     # Generic venue names (risky)
    
    generic_keywords = ['downtown', 'city hall', 'park', 'arena', 'center', 'tba', 'tbd']
    
    for event in events:
        has_address = bool(event.address and event.address.strip())
        has_venue = bool(event.venue and event.venue.strip())
        has_city = bool(event.city and event.city.strip())
        
        if has_address and has_city:
            complete_data.append(event)
        elif has_venue and not has_address:
            # Check if venue is generic
            venue_lower = event.venue.lower()
            if any(keyword in venue_lower for keyword in generic_keywords):
                generic_venues.append(event)
            else:
                venue_only.append(event)
        else:
            missing_location.append(event)
    
    # Print summary
    print(f"✅ Complete Location Data (address + city): {len(complete_data)}")
    print(f"   → Maps will be 100% accurate\n")
    
    print(f"⚠️  Venue Name Only (no address): {len(venue_only)}")
    print(f"   → Maps may be accurate if venue is well-known")
    if venue_only:
        print(f"   Sample venues:")
        for event in venue_only[:5]:
            print(f"   - {event.venue} ({event.title[:40]}...)")
        if len(venue_only) > 5:
            print(f"   ... and {len(venue_only) - 5} more")
    print()
    
    print(f"❌ Generic/Risky Venue Names: {len(generic_venues)}")
    print(f"   → Maps will likely be INACCURATE - skip these")
    if generic_venues:
        print(f"   Sample venues:")
        for event in generic_venues[:5]:
            print(f"   - {event.venue} ({event.title[:40]}...)")
    print()
    
    print(f"🚫 Missing Location Data: {len(missing_location)}")
    print(f"   → Cannot show maps for these events")
    if missing_location:
        print(f"   Sample events:")
        for event in missing_location[:5]:
            print(f"   - {event.title[:60]}")
    print()
    
    # Calculate percentages
    total = len(events)
    accurate_maps = len(complete_data)
    maybe_accurate = len(venue_only)
    no_maps = len(generic_venues) + len(missing_location)
    
    print("=" * 60)
    print("📈 Map Accuracy Forecast:")
    print(f"   {accurate_maps}/{total} ({accurate_maps/total*100:.1f}%) - Accurate maps")
    print(f"   {maybe_accurate}/{total} ({maybe_accurate/total*100:.1f}%) - Probably accurate")
    print(f"   {no_maps}/{total} ({no_maps/total*100:.1f}%) - Will skip maps")
    print()
    
    if no_maps / total > 0.3:
        print("⚠️  WARNING: >30% of events have poor location data")
        print("💡 Recommendation: Add geocoding API for better accuracy")
    else:
        print("✅ Location data quality is good!")
    
    db.close()

if __name__ == "__main__":
    validate_locations()

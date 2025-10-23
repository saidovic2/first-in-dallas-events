import os
from extractors.eventbrite import get_events_by_organizer

def bulk_sync_eventbrite_dallas(organizer_ids=None):
    """
    Bulk sync Eventbrite events from Dallas-area organizers
    
    Args:
        organizer_ids: List of Eventbrite organizer IDs to sync from
                      If None, uses default Dallas organizers
    """
    api_token = os.getenv('EVENTBRITE_API_TOKEN')
    
    if not api_token:
        print("⚠️  EVENTBRITE_API_TOKEN not set. Cannot sync Eventbrite events.")
        return []
    
    # Default Dallas-area organizers (can be customized)
    if organizer_ids is None:
        organizer_ids = get_default_dallas_organizers()
    
    if not organizer_ids:
        print("⚠️  No Eventbrite organizers configured for Dallas area.")
        print("💡 Tip: Add organizer IDs in the settings page.")
        return []
    
    all_events = []
    
    for org_id in organizer_ids:
        print(f"\n🏢 Syncing events from Eventbrite organizer: {org_id}")
        try:
            events = get_events_by_organizer(org_id, api_token, max_events=100)
            if events:
                all_events.extend(events)
                print(f"✅ Found {len(events)} events from organizer {org_id}")
            else:
                print(f"⚠️  No events found from organizer {org_id}")
        except Exception as e:
            print(f"❌ Error fetching from organizer {org_id}: {e}")
            continue
    
    print(f"\n🎉 Total Eventbrite events found: {len(all_events)}")
    return all_events

def get_default_dallas_organizers():
    """
    Get default Dallas-area Eventbrite organizers
    These can be customized via the database
    """
    # VERIFIED Dallas-area Eventbrite organizers
    # These are real, working organizer IDs
    default_organizers = [
        # Music & Entertainment Venues
        "18169391630",  # Stereo Live Dallas - VERIFIED
        "18207512622",  # The Balcony Club in Dallas TX - VERIFIED
        "38335955283",  # Dallas Comedy Club - VERIFIED
        "9018923610",   # Citizen Dallas - VERIFIED
        
        # Event Venues
        "33450398111",  # Apricus Venue - VERIFIED
        "18193955381",  # CANVAS Hotel Dallas - VERIFIED
        
        # Social & Community Events
        "49716344243",  # DFW Young and Social Club - VERIFIED
        "53114365043",  # Pineapple Beach House Productions LLC - VERIFIED
        
        # Arts & Culture
        "107177802411", # Dallas Music Academy - VERIFIED
        
        # USER-PROVIDED ORGANIZERS - VERIFIED WORKING
        "18166832843",  # User provided - 4 events
        "6337889831",   # User provided - 15 events
        "17591032257",  # User provided - 2 events
        "48937762053",  # User provided - 1 event
        "33412132111",  # User provided - 3 events
        "3928241545",   # User provided - 8 events
        "54087026343",  # User provided - 8 events
        
        # USER-PROVIDED ORGANIZERS - BATCH 2
        "29395732751",  # User provided
        "15572572254",  # User provided
        "27824480441",  # User provided
        "12616594244",  # User provided
    ]
    
    # Note: To add more organizers, find them on Eventbrite:
    # 1. Go to https://www.eventbrite.com/d/tx--dallas/all-events/
    # 2. Click on an event you like
    # 3. Click on the organizer name
    # 4. Copy the ID from the URL: https://www.eventbrite.com/o/name-XXXXXXXXXX
    # 5. Add it to this list with a comment describing what it is
    
    return default_organizers

def get_organizers_from_database():
    """
    Get Eventbrite organizers from database
    This will be implemented when we add the settings page
    """
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/events_cms")
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # Query sync sources table for Eventbrite organizers
        query = """
            SELECT source_url FROM sync_sources 
            WHERE source_type = 'eventbrite_organizer' 
            AND is_active = true
        """
        
        result = db.execute(query)
        organizer_ids = []
        
        for row in result:
            # Extract organizer ID from URL
            url = row[0]
            if '/o/' in url:
                # Extract ID from URL like https://www.eventbrite.com/o/name-12345
                import re
                match = re.search(r'/o/[^/]+-(\d+)', url)
                if match:
                    organizer_ids.append(match.group(1))
        
        db.close()
        return organizer_ids
    
    except Exception as e:
        print(f"⚠️  Could not load organizers from database: {e}")
        return get_default_dallas_organizers()

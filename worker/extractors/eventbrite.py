import os
import requests
from datetime import datetime
from dateutil import parser as date_parser

def extract_eventbrite_events(url_or_query):
    """
    Extract events from Eventbrite using their official API
    Can accept:
    - Single event URL: https://www.eventbrite.com/e/event-name-123456789
    - Search query: "Dallas, TX" or "concerts in Dallas"
    - Organization ID: org_123456
    """
    api_token = os.getenv('EVENTBRITE_API_TOKEN')
    
    if not api_token:
        print("⚠️  EVENTBRITE_API_TOKEN not set. Skipping Eventbrite extraction.")
        return None
    
    try:
        # Determine if it's a URL or search query
        if 'eventbrite.com/e/' in url_or_query:
            # Single event URL
            event_id = extract_event_id_from_url(url_or_query)
            if event_id:
                return [get_event_by_id(event_id, api_token)]
        elif 'eventbrite.com/o/' in url_or_query:
            # Organization URL
            org_id = extract_org_id_from_url(url_or_query)
            if org_id:
                return get_events_by_organizer(org_id, api_token)
        elif 'eventbrite.com/d/' in url_or_query:
            # Location search URL (e.g., /d/tx--dallas/events/)
            location = extract_location_from_url(url_or_query)
            return search_events_by_location(location, api_token)
        else:
            # Treat as search query
            return search_events(url_or_query, api_token)
    
    except Exception as e:
        print(f"❌ Error extracting from Eventbrite: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_event_id_from_url(url):
    """Extract event ID from Eventbrite URL"""
    import re
    # Pattern: /e/event-name-123456789
    match = re.search(r'/e/[^/]+-(\d+)', url)
    if match:
        return match.group(1)
    return None

def extract_org_id_from_url(url):
    """Extract organization ID from Eventbrite URL"""
    import re
    # Pattern: /o/org-name-123456789
    match = re.search(r'/o/[^/]+-(\d+)', url)
    if match:
        return match.group(1)
    return None

def extract_location_from_url(url):
    """Extract location from Eventbrite directory URL"""
    import re
    # Pattern: /d/tx--dallas/events/
    match = re.search(r'/d/([^/]+)/', url)
    if match:
        location_slug = match.group(1)
        # Convert slug to readable location (tx--dallas -> Dallas, TX)
        parts = location_slug.split('--')
        if len(parts) == 2:
            state = parts[0].upper()
            city = parts[1].replace('-', ' ').title()
            return f"{city}, {state}"
    return "Dallas, TX"  # Default

def get_event_by_id(event_id, api_token):
    """Get a single event by ID"""
    print(f"🎫 Fetching Eventbrite event: {event_id}")
    
    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/"
    params = {
        'token': api_token,  # Use token as query parameter
        'expand': 'venue,organizer,ticket_availability'
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    event_data = response.json()
    return parse_eventbrite_event(event_data)

def get_events_by_organizer(org_id, api_token, max_events=50):
    """Get events from a specific organizer"""
    print(f"🏢 Fetching events from organizer: {org_id}")
    
    url = f"https://www.eventbriteapi.com/v3/organizers/{org_id}/events/"
    params = {
        'token': api_token,  # Use token as query parameter
        'expand': 'venue,ticket_availability',
        'status': 'live',
        'order_by': 'start_asc'
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    events = []
    
    for event_data in data.get('events', [])[:max_events]:
        event = parse_eventbrite_event(event_data)
        if event:
            events.append(event)
    
    print(f"✅ Found {len(events)} events from organizer")
    return events

def search_events_by_location(location, api_token, max_events=50):
    """Search events by location"""
    print(f"🔍 Searching Eventbrite events in: {location}")
    
    # Note: Event search endpoint requires OAuth, not just API key
    # For now, we'll skip location search and suggest using organizer URLs instead
    print("⚠️  Location search requires OAuth authentication.")
    print("💡 Tip: Use organizer URLs or specific event URLs instead.")
    return []
    
    data = response.json()
    events = []
    
    for event_data in data.get('events', [])[:max_events]:
        event = parse_eventbrite_event(event_data)
        if event:
            events.append(event)
    
    print(f"✅ Found {len(events)} events in {location}")
    return events

def search_events(query, api_token, max_events=50):
    """Search events by keyword"""
    print(f"🔍 Searching Eventbrite for: {query}")
    
    # Note: Event search endpoint requires OAuth, not just API key
    print("⚠️  Keyword search requires OAuth authentication.")
    print("💡 Tip: Use organizer URLs or specific event URLs instead.")
    return []
    
    data = response.json()
    events = []
    
    for event_data in data.get('events', [])[:max_events]:
        event = parse_eventbrite_event(event_data)
        if event:
            events.append(event)
    
    print(f"✅ Found {len(events)} events for '{query}'")
    return events

def parse_eventbrite_event(data):
    """Parse Eventbrite event data into our format"""
    try:
        # Extract basic info
        title = data.get('name', {}).get('text')
        description = data.get('description', {}).get('text') or data.get('summary')
        event_url = data.get('url')  # Eventbrite event URL
        
        if not title:
            return None
        
        # Parse dates
        start_at = None
        end_at = None
        
        start_data = data.get('start', {})
        if start_data.get('utc'):
            start_at = date_parser.parse(start_data['utc'])
        
        end_data = data.get('end', {})
        if end_data.get('utc'):
            end_at = date_parser.parse(end_data['utc'])
        
        # Extract venue
        venue = None
        address = None
        city = None
        
        venue_data = data.get('venue')
        if venue_data:
            venue = venue_data.get('name')
            address_data = venue_data.get('address', {})
            address = address_data.get('address_1')
            city = address_data.get('city')
        
        # Extract pricing
        price_tier = 'FREE'
        price_amount = None
        
        is_free = data.get('is_free', False)
        if not is_free:
            price_tier = 'PAID'
            # Try to get ticket price
            ticket_availability = data.get('ticket_availability')
            if ticket_availability:
                min_price = ticket_availability.get('minimum_ticket_price')
                if min_price:
                    price_amount = float(min_price.get('major_value', 0))
        
        # Extract image
        image_url = None
        logo = data.get('logo')
        if logo:
            image_url = logo.get('original', {}).get('url')
        
        event = {
            'title': title,
            'description': description,
            'start_at': start_at,
            'end_at': end_at,
            'venue': venue,
            'address': address,
            'city': city,
            'price_tier': price_tier,
            'price_amount': price_amount,
            'image_url': image_url,
            'source_url': event_url
        }
        
        return event
    
    except Exception as e:
        print(f"❌ Error parsing Eventbrite event: {e}")
        return None

def detect_category_from_eventbrite(data, title, description):
    """Detect category from Eventbrite data"""
    # Eventbrite provides category info
    category_data = data.get('category')
    if category_data:
        category_name = category_data.get('name', '')
        # Map Eventbrite categories to our categories
        category_mapping = {
            'Music': 'Music',
            'Business & Professional': 'Business',
            'Food & Drink': 'Food & Drink',
            'Community & Culture': 'Community',
            'Performing & Visual Arts': 'Arts',
            'Film, Media & Entertainment': 'Film',
            'Sports & Fitness': 'Sports',
            'Health & Wellness': 'Health',
            'Science & Technology': 'Business',
            'Travel & Outdoor': 'Other',
            'Charity & Causes': 'Community',
            'Religion & Spirituality': 'Community',
            'Family & Education': 'Family',
            'Seasonal & Holiday': 'Other',
            'Government & Politics': 'Community',
            'Fashion & Beauty': 'Other',
            'Home & Lifestyle': 'Other',
            'Auto, Boat & Air': 'Other',
            'Hobbies & Special Interest': 'Other',
            'Other': 'Other'
        }
        
        for eb_cat, our_cat in category_mapping.items():
            if eb_cat.lower() in category_name.lower():
                return our_cat
    
    # Fallback to keyword detection from title and description
    text = f"{title} {description}".lower()
    
    # Keyword-based category detection
    if any(word in text for word in ['concert', 'music', 'band', 'singer', 'dj', 'festival']):
        return 'Music'
    elif any(word in text for word in ['comedy', 'standup', 'stand-up', 'comedian', 'improv']):
        return 'Comedy'
    elif any(word in text for word in ['art', 'gallery', 'exhibition', 'museum', 'theater', 'theatre', 'performance']):
        return 'Arts'
    elif any(word in text for word in ['sports', 'game', 'match', 'tournament', 'race', 'fitness']):
        return 'Sports'
    elif any(word in text for word in ['food', 'drink', 'dining', 'restaurant', 'tasting', 'culinary']):
        return 'Food & Drink'
    elif any(word in text for word in ['business', 'networking', 'conference', 'seminar', 'workshop']):
        return 'Business'
    elif any(word in text for word in ['family', 'kids', 'children']):
        return 'Family'
    elif any(word in text for word in ['film', 'movie', 'cinema', 'screening']):
        return 'Film'
    elif any(word in text for word in ['community', 'charity', 'fundraiser', 'volunteer']):
        return 'Community'
    
    return 'Other'

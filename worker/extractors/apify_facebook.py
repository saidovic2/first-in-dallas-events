import os
import requests
import time
import re
from datetime import datetime
from dateutil import parser as date_parser

def detect_event_category(title, description):
    """
    Detect event category based on title and description keywords
    """
    text = f"{title or ''} {description or ''}".lower()
    
    # Category keywords mapping
    categories = {
        'Music': ['concert', 'music', 'band', 'tour', 'festival', 'live music', 'performance', 'show', 'singer', 'dj', 'acoustic'],
        'Sports': ['game', 'match', 'tournament', 'championship', 'sports', 'football', 'basketball', 'baseball', 'soccer', 'hockey'],
        'Arts': ['art', 'gallery', 'exhibition', 'museum', 'theater', 'theatre', 'play', 'opera', 'ballet', 'dance'],
        'Food & Drink': ['food', 'wine', 'beer', 'tasting', 'dinner', 'brunch', 'restaurant', 'cooking', 'culinary', 'brewery'],
        'Business': ['conference', 'seminar', 'workshop', 'networking', 'business', 'professional', 'summit', 'meetup'],
        'Community': ['community', 'charity', 'fundraiser', 'volunteer', 'nonprofit', 'awareness', 'rally'],
        'Family': ['family', 'kids', 'children', 'family-friendly', 'all ages'],
        'Nightlife': ['party', 'club', 'nightclub', 'bar', 'lounge', 'happy hour', 'night out'],
        'Education': ['class', 'course', 'training', 'lecture', 'educational', 'learning', 'study'],
        'Health': ['yoga', 'fitness', 'wellness', 'health', 'meditation', 'workout', 'gym'],
        'Film': ['movie', 'film', 'screening', 'cinema', 'premiere'],
        'Comedy': ['comedy', 'stand-up', 'comedian', 'improv', 'funny'],
    }
    
    # Count matches for each category
    category_scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            category_scores[category] = score
    
    # Return category with highest score, or 'Other' if no matches
    if category_scores:
        return max(category_scores, key=category_scores.get)
    
    return 'Other'

def extract_facebook_with_apify(url):
    """
    Extract Facebook event using Apify's Facebook Events Scraper
    Requires APIFY_API_TOKEN environment variable
    """
    api_token = os.getenv('APIFY_API_TOKEN')
    
    if not api_token:
        print("⚠️  APIFY_API_TOKEN not set. Falling back to basic scraper.")
        return None
    
    try:
        print(f"🚀 Using Apify to scrape: {url}")
        
        # Apify Actor ID from the API documentation
        # Correct format: apify~facebook-events-scraper (with tilde)
        actor_id = "apify~facebook-events-scraper"
        
        # Prepare the input for Apify
        # The Actor expects startUrls as an array of URL strings, not objects
        run_input = {
            "startUrls": [url],  # Just the URL string, not wrapped in an object
            "maxResults": 1,
            "proxyConfiguration": {
                "useApifyProxy": True
            }
        }
        
        # Start the Apify actor run using the correct API format from documentation
        run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        print("📤 Starting Apify actor...")
        response = requests.post(run_url, json=run_input, headers=headers, timeout=30)
        response.raise_for_status()
        
        run_data = response.json()
        run_id = run_data["data"]["id"]
        
        print(f"⏳ Waiting for Apify to complete (Run ID: {run_id})...")
        
        # Wait for the run to complete (max 2 minutes)
        max_wait = 120  # seconds
        wait_interval = 5  # seconds
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval
            
            # Check run status
            status_url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}"
            status_response = requests.get(status_url, headers=headers, timeout=10)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            status = status_data["data"]["status"]
            
            print(f"⏳ Status: {status} ({elapsed}s elapsed)")
            
            if status == "SUCCEEDED":
                print("✅ Apify scraping completed!")
                break
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                print(f"❌ Apify run failed with status: {status}")
                return None
        
        if elapsed >= max_wait:
            print("⏰ Apify run timed out")
            return None
        
        # Get the results from the dataset
        dataset_id = status_data["data"]["defaultDatasetId"]
        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        
        print("📥 Fetching results...")
        results_response = requests.get(dataset_url, headers=headers, timeout=10)
        results_response.raise_for_status()
        
        results = results_response.json()
        
        if not results:
            print("❌ No events found by Apify")
            return None
        
        # Parse the Apify results into our event format
        events = []
        for item in results:
            event = parse_apify_event(item, url)
            if event:
                events.append(event)
        
        print(f"✅ Extracted {len(events)} event(s) from Apify")
        return events
    
    except Exception as e:
        print(f"❌ Error using Apify: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_apify_event(data, source_url):
    """Parse Apify Facebook event data into our format"""
    try:
        # Debug: Print what Apify returned
        print(f"📋 Apify data keys: {list(data.keys())}")
        
        # Check if Apify returned an error
        if 'error' in data:
            print(f"❌ Apify Error: {data.get('error')}")
            if 'errorDescription' in data:
                print(f"📝 Error Description: {data.get('errorDescription')}")
            return None
        
        event = {
            'title': data.get('name') or data.get('title'),
            'description': data.get('description'),
            'start_at': None,
            'end_at': None,
            'venue': None,
            'address': None,
            'city': None,
            'price_tier': 'FREE',  # Will be updated below (uppercase for DB enum)
            'price_amount': None,
            'image_url': None,
            'category': None  # Will be detected below
        }
        
        # Parse start date
        start_time = data.get('startTime') or data.get('start_time')
        if start_time:
            try:
                event['start_at'] = date_parser.parse(start_time)
            except:
                pass
        
        # Parse end date
        end_time = data.get('endTime') or data.get('end_time')
        if end_time:
            try:
                event['end_at'] = date_parser.parse(end_time)
            except:
                pass
        
        # Extract location
        location = data.get('location') or data.get('place')
        if location:
            if isinstance(location, dict):
                event['venue'] = location.get('name')
                city_value = location.get('city')
                # Normalize city - remove ", TX" or state suffix for consistency
                event['city'] = city_value.replace(', TX', '').replace(' TX', '') if city_value else None
                event['address'] = location.get('street') or location.get('address')
            elif isinstance(location, str):
                event['venue'] = location
                # Try to extract city from location string
                if ',' in location:
                    parts = location.split(',')
                    city_value = parts[-1].strip()
                    # Normalize city - remove state suffix
                    event['city'] = city_value.replace(', TX', '').replace(' TX', '')
        
        # Extract image - try multiple field names
        photo = (data.get('photo') or data.get('image') or data.get('cover') or 
                 data.get('photoUrl') or data.get('imageUrl') or data.get('coverPhoto'))
        
        print(f"🖼️  Photo data: {photo}")
        
        if photo:
            if isinstance(photo, dict):
                event['image_url'] = photo.get('url') or photo.get('source') or photo.get('src')
            elif isinstance(photo, str):
                event['image_url'] = photo
        
        print(f"🖼️  Final image_url: {event['image_url']}")
        
        # Extract pricing information
        ticket_url = data.get('ticketUrl') or data.get('ticket_url')
        is_online = data.get('isOnline', False)
        
        # Check if event has tickets/pricing
        if ticket_url or 'ticket' in str(event['description']).lower():
            event['price_tier'] = 'PAID'
            # Try to extract price from description
            if event['description']:
                # Look for price patterns like $20, $15-$25, etc.
                price_match = re.search(r'\$(\d+(?:\.\d{2})?)', event['description'])
                if price_match:
                    try:
                        event['price_amount'] = float(price_match.group(1))
                    except:
                        pass
        
        # Detect category from event data
        category = data.get('category') or data.get('type')
        
        if category:
            event['category'] = category
        else:
            # Smart category detection based on title and description
            event['category'] = detect_event_category(event['title'], event['description'])
        
        # Extract interested count (optional, for stats)
        interested = data.get('usersInterested') or data.get('interested_count')
        if interested:
            # You could add this to description or a custom field
            if event['description']:
                event['description'] += f"\n\n👥 {interested} people interested"
            else:
                event['description'] = f"👥 {interested} people interested"
        
        # Check if we have minimum required data
        if not event['title'] or not event['start_at']:
            print(f"⚠️  Skipping event - missing title or start date")
            return None
        
        return event
    
    except Exception as e:
        print(f"❌ Error parsing Apify event: {e}")
        return None

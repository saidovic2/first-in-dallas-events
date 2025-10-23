import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser

def extract_json_ld(url):
    """Extract event data from JSON-LD structured data"""
    events = []
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all JSON-LD scripts
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle both single objects and arrays
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    # Check if it's an Event type
                    item_type = item.get('@type', '')
                    if item_type == 'Event' or (isinstance(item_type, list) and 'Event' in item_type):
                        event = parse_json_ld_event(item)
                        if event:
                            events.append(event)
            
            except json.JSONDecodeError:
                continue
    
    except Exception as e:
        print(f"Error extracting JSON-LD from {url}: {e}")
    
    return events

def parse_json_ld_event(data):
    """Parse a single JSON-LD Event object"""
    try:
        # Required fields
        title = data.get('name')
        start_date = data.get('startDate')
        
        if not title or not start_date:
            return None
        
        # Parse dates
        start_at = date_parser.parse(start_date)
        end_at = None
        if data.get('endDate'):
            end_at = date_parser.parse(data['endDate'])
        
        # Extract location
        location = data.get('location', {})
        venue = None
        address = None
        city = None
        
        if isinstance(location, dict):
            venue = location.get('name')
            address_data = location.get('address', {})
            if isinstance(address_data, dict):
                address = address_data.get('streetAddress')
                city = address_data.get('addressLocality')
            elif isinstance(address_data, str):
                address = address_data
        
        # Extract price
        price_tier = "free"
        price_amount = None
        offers = data.get('offers', {})
        if isinstance(offers, dict):
            price = offers.get('price')
            if price and float(price) > 0:
                price_tier = "paid"
                price_amount = float(price)
        
        # Extract image
        image_url = None
        image = data.get('image')
        if image:
            if isinstance(image, str):
                image_url = image
            elif isinstance(image, list) and len(image) > 0:
                image_url = image[0] if isinstance(image[0], str) else image[0].get('url')
            elif isinstance(image, dict):
                image_url = image.get('url')
        
        # Extract description
        description = data.get('description')
        
        # Extract category
        category = None
        event_type = data.get('eventType') or data.get('category')
        if event_type:
            category = event_type if isinstance(event_type, str) else event_type[0]
        
        return {
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
            'category': category
        }
    
    except Exception as e:
        print(f"Error parsing JSON-LD event: {e}")
        return None

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser

def extract_facebook_event(url):
    """
    Extract event data from Facebook event pages
    Uses multiple fallback methods since Facebook blocks automated scraping
    """
    events = []
    
    try:
        # Method 1: Try to get event ID and use Facebook Graph API (if available)
        event_id = extract_event_id(url)
        if event_id:
            # Try Graph API (requires access token - optional)
            # For now, we'll use web scraping
            pass
        
        # Method 2: Web scraping with proper headers
        event = scrape_facebook_page(url)
        if event:
            events.append(event)
    
    except Exception as e:
        print(f"Error extracting Facebook event from {url}: {e}")
    
    return events

def extract_event_id(url):
    """Extract Facebook event ID from URL"""
    # Pattern: /events/123456789
    match = re.search(r'/events/(\d+)', url)
    if match:
        return match.group(1)
    return None

def scrape_facebook_page(url):
    """Scrape Facebook event page using requests + BeautifulSoup"""
    try:
        # Use mobile Facebook URL (simpler HTML, less JavaScript)
        if 'facebook.com' in url and 'm.facebook.com' not in url:
            url = url.replace('www.facebook.com', 'm.facebook.com')
            url = url.replace('facebook.com', 'm.facebook.com')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract from meta tags (Open Graph)
        event = extract_from_meta_tags(soup, url)
        
        # Try to extract from page content
        if not event or not event.get('title'):
            event = extract_from_page_content(soup, url)
        
        return event
    
    except Exception as e:
        print(f"Error scraping Facebook page: {e}")
        return None

def extract_from_meta_tags(soup, url):
    """Extract event data from Open Graph meta tags"""
    event = {
        'title': None,
        'description': None,
        'start_at': None,
        'end_at': None,
        'venue': None,
        'address': None,
        'city': None,
        'price_tier': 'free',
        'price_amount': None,
        'image_url': None,
        'category': 'Social'
    }
    
    # Extract title
    og_title = soup.find('meta', property='og:title')
    if og_title:
        event['title'] = og_title.get('content')
    
    # Extract description
    og_description = soup.find('meta', property='og:description')
    if og_description:
        event['description'] = og_description.get('content')
    
    # Extract image
    og_image = soup.find('meta', property='og:image')
    if og_image:
        event['image_url'] = og_image.get('content')
    
    # Try to find event:start_time
    event_start = soup.find('meta', property='event:start_time')
    if event_start:
        try:
            event['start_at'] = date_parser.parse(event_start.get('content'))
        except:
            pass
    
    # Try to find event:end_time
    event_end = soup.find('meta', property='event:end_time')
    if event_end:
        try:
            event['end_at'] = date_parser.parse(event_end.get('content'))
        except:
            pass
    
    # Try to find location
    event_location = soup.find('meta', property='event:location')
    if event_location:
        location_text = event_location.get('content')
        event['venue'] = location_text
        # Try to extract city from location
        if ',' in location_text:
            parts = location_text.split(',')
            if len(parts) >= 2:
                event['city'] = parts[-1].strip()
    
    return event if event['title'] else None

def extract_from_page_content(soup, url):
    """Extract event data from page HTML content"""
    event = {
        'title': None,
        'description': None,
        'start_at': None,
        'end_at': None,
        'venue': None,
        'address': None,
        'city': None,
        'price_tier': 'free',
        'price_amount': None,
        'image_url': None,
        'category': 'Social'
    }
    
    # Try to find title in h1 or title tag
    title_tag = soup.find('h1') or soup.find('title')
    if title_tag:
        event['title'] = title_tag.get_text(strip=True)
    
    # Try to find description
    desc_div = soup.find('div', {'data-testid': 'event-description'})
    if desc_div:
        event['description'] = desc_div.get_text(strip=True)
    
    # Try to find date/time patterns in text
    text_content = soup.get_text()
    
    # Look for date patterns
    date_patterns = [
        r'(\w+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [AP]M)',
        r'(\w+ \d{1,2} at \d{1,2}:\d{2} [AP]M)',
        r'(\d{1,2}/\d{1,2}/\d{4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_content)
        if match:
            try:
                event['start_at'] = date_parser.parse(match.group(1))
                break
            except:
                continue
    
    # If still no start date, use a placeholder
    if not event['start_at']:
        # Set to tomorrow as placeholder
        from datetime import timedelta
        event['start_at'] = datetime.now() + timedelta(days=1)
    
    return event if event['title'] else None

def extract_with_graph_api(event_id, access_token=None):
    """
    Extract event using Facebook Graph API
    Requires a valid Facebook access token
    """
    if not access_token:
        return None
    
    try:
        api_url = f"https://graph.facebook.com/v18.0/{event_id}"
        params = {
            'access_token': access_token,
            'fields': 'name,description,start_time,end_time,place,cover,ticket_uri,is_online'
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        event = {
            'title': data.get('name'),
            'description': data.get('description'),
            'start_at': None,
            'end_at': None,
            'venue': None,
            'address': None,
            'city': None,
            'price_tier': 'free',
            'price_amount': None,
            'image_url': None,
            'category': 'Social'
        }
        
        # Parse dates
        if data.get('start_time'):
            event['start_at'] = date_parser.parse(data['start_time'])
        if data.get('end_time'):
            event['end_at'] = date_parser.parse(data['end_time'])
        
        # Extract location
        place = data.get('place', {})
        if place:
            event['venue'] = place.get('name')
            location = place.get('location', {})
            event['city'] = location.get('city')
            event['address'] = location.get('street')
        
        # Extract image
        cover = data.get('cover', {})
        if cover:
            event['image_url'] = cover.get('source')
        
        return event
    
    except Exception as e:
        print(f"Error using Graph API: {e}")
        return None

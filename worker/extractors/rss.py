import feedparser
from datetime import datetime
from dateutil import parser as date_parser

def extract_rss(url):
    """Extract events from RSS/Atom feed"""
    events = []
    
    try:
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            # Try to extract date
            start_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                start_at = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                start_at = datetime(*entry.updated_parsed[:6])
            
            if not start_at:
                continue
            
            # Extract description
            description = None
            if hasattr(entry, 'summary'):
                description = entry.summary
            elif hasattr(entry, 'description'):
                description = entry.description
            
            # Extract image
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                image_url = entry.enclosures[0].get('href')
            
            event_data = {
                'title': entry.title,
                'description': description,
                'start_at': start_at,
                'end_at': None,
                'venue': None,
                'address': None,
                'city': None,
                'price_tier': 'free',
                'price_amount': None,
                'image_url': image_url,
                'category': entry.get('category') or (entry.tags[0].term if hasattr(entry, 'tags') and entry.tags else None)
            }
            
            events.append(event_data)
    
    except Exception as e:
        print(f"Error extracting RSS from {url}: {e}")
    
    return events

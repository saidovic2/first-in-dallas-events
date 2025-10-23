import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
import re

def extract_html_fallback(url):
    """Fallback HTML extraction using meta tags and heuristics"""
    events = []
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try Open Graph tags
        title = None
        description = None
        image_url = None
        
        og_title = soup.find('meta', property='og:title')
        if og_title:
            title = og_title.get('content')
        
        og_description = soup.find('meta', property='og:description')
        if og_description:
            description = og_description.get('content')
        
        og_image = soup.find('meta', property='og:image')
        if og_image:
            image_url = og_image.get('content')
        
        # Fallback to regular meta tags
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.string
        
        if not description:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content')
        
        # Try to find date in text
        start_at = None
        text_content = soup.get_text()
        
        # Look for common date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                try:
                    start_at = date_parser.parse(match.group())
                    break
                except:
                    continue
        
        # Only create event if we have minimum required data
        if title and start_at:
            event_data = {
                'title': title,
                'description': description,
                'start_at': start_at,
                'end_at': None,
                'venue': None,
                'address': None,
                'city': None,
                'price_tier': 'free',
                'price_amount': None,
                'image_url': image_url,
                'category': None
            }
            events.append(event_data)
    
    except Exception as e:
        print(f"Error extracting HTML from {url}: {e}")
    
    return events

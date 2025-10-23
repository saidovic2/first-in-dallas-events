import requests
from ics import Calendar
from datetime import datetime

def extract_ics(url):
    """Extract events from ICS/iCal file"""
    events = []
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        calendar = Calendar(response.text)
        
        for event in calendar.events:
            event_data = {
                'title': event.name,
                'description': event.description,
                'start_at': event.begin.datetime if event.begin else None,
                'end_at': event.end.datetime if event.end else None,
                'venue': event.location,
                'address': event.location,
                'city': None,  # ICS doesn't typically have structured city data
                'price_tier': 'free',
                'price_amount': None,
                'image_url': None,
                'category': None
            }
            
            if event_data['start_at']:
                events.append(event_data)
    
    except Exception as e:
        print(f"Error extracting ICS from {url}: {e}")
    
    return events

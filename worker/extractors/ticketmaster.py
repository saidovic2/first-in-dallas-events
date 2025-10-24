"""
Ticketmaster API Integration
Fetches events from Ticketmaster Discovery API for Dallas area
Includes affiliate tracking for commission earnings
"""

import os
import requests
from datetime import datetime
from typing import List, Dict, Optional

class TicketmasterExtractor:
    """Extract events from Ticketmaster API"""
    
    def __init__(self):
        self.api_key = os.getenv('TICKETMASTER_API_KEY')
        self.affiliate_id = os.getenv('TICKETMASTER_AFFILIATE_ID')
        self.base_url = 'https://app.ticketmaster.com/discovery/v2'
        
        if not self.api_key:
            raise ValueError("TICKETMASTER_API_KEY not found in environment variables")
    
    def fetch_events(
        self, 
        city: str = "Dallas", 
        state: str = "TX",
        radius: int = 50,
        size: int = 200
    ) -> List[Dict]:
        """
        Fetch events from Ticketmaster for specified city
        
        Args:
            city: City name (default: Dallas)
            state: State code (default: TX)
            radius: Search radius in miles (default: 50)
            size: Number of events to fetch (max: 200)
        
        Returns:
            List of event dictionaries
        """
        print(f"🎫 Fetching Ticketmaster events for {city}, {state}...")
        
        params = {
            'apikey': self.api_key,
            'city': city,
            'stateCode': state,
            'radius': radius,
            'size': size,
            'sort': 'date,asc'
        }
        
        try:
            response = requests.get(
                f'{self.base_url}/events.json',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if '_embedded' not in data or 'events' not in data['_embedded']:
                print("⚠️  No events found in Ticketmaster response")
                return []
            
            raw_events = data['_embedded']['events']
            print(f"✅ Found {len(raw_events)} events from Ticketmaster")
            
            # Parse events
            events = []
            for event in raw_events:
                parsed = self._parse_event(event)
                if parsed:
                    events.append(parsed)
            
            print(f"✅ Successfully parsed {len(events)} Ticketmaster events")
            return events
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching Ticketmaster events: {e}")
            return []
    
    def _parse_event(self, event: Dict) -> Optional[Dict]:
        """Parse Ticketmaster event into our format"""
        try:
            # Title
            title = event.get('name')
            if not title:
                return None
            
            # Dates
            dates = event.get('dates', {})
            start_data = dates.get('start', {})
            start_date_str = start_data.get('dateTime') or start_data.get('localDate')
            
            if not start_date_str:
                return None
            
            # Parse start date
            try:
                if 'T' in start_date_str:
                    start_at = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                else:
                    start_at = datetime.strptime(start_date_str, '%Y-%m-%d')
            except:
                return None
            
            # Venue information
            venue_name = None
            address = None
            city = None
            
            if '_embedded' in event and 'venues' in event['_embedded']:
                venue = event['_embedded']['venues'][0]
                venue_name = venue.get('name')
                
                if 'address' in venue:
                    address = venue['address'].get('line1')
                
                if 'city' in venue:
                    city = venue['city'].get('name')
            
            # Price information
            price_tier = 'PAID'
            price_amount = None
            
            if 'priceRanges' in event and event['priceRanges']:
                price_range = event['priceRanges'][0]
                min_price = price_range.get('min', 0)
                
                if min_price == 0:
                    price_tier = 'FREE'
                else:
                    price_amount = str(min_price)
            
            # Image
            image_url = None
            if 'images' in event and event['images']:
                # Get highest quality image
                images = sorted(event['images'], key=lambda x: x.get('width', 0), reverse=True)
                image_url = images[0].get('url')
            
            # Category
            category = None
            if 'classifications' in event and event['classifications']:
                classification = event['classifications'][0]
                segment = classification.get('segment', {}).get('name')
                genre = classification.get('genre', {}).get('name')
                
                # Map to our categories
                category_map = {
                    'Music': 'Music',
                    'Sports': 'Sports',
                    'Arts & Theatre': 'Arts',
                    'Film': 'Film',
                    'Miscellaneous': 'Other'
                }
                category = category_map.get(segment, genre or 'Other')
            
            # Event URL with affiliate tracking
            event_url = event.get('url', '')
            if event_url and self.affiliate_id:
                # Add affiliate tracking to URL
                separator = '&' if '?' in event_url else '?'
                event_url = f"{event_url}{separator}CAMEFROM=CMPAFFILIATE_{self.affiliate_id}"
            
            # Description
            description = None
            if 'info' in event:
                description = event['info']
            elif 'pleaseNote' in event:
                description = event['pleaseNote']
            
            # Build event dictionary
            parsed_event = {
                'title': title,
                'description': description,
                'start_at': start_at.isoformat(),
                'end_at': None,  # Ticketmaster doesn't provide end times
                'venue': venue_name,
                'address': address,
                'city': city,
                'price_tier': price_tier.lower(),
                'price_amount': price_amount,
                'image_url': image_url,
                'source_url': event_url,
                'source_type': 'ticketmaster',
                'category': category,
            }
            
            return parsed_event
            
        except Exception as e:
            print(f"⚠️  Error parsing Ticketmaster event: {e}")
            return None


def extract_ticketmaster_events(city: str = "Dallas", state: str = "TX") -> List[Dict]:
    """
    Main function to extract Ticketmaster events
    
    Args:
        city: City name
        state: State code
    
    Returns:
        List of parsed events
    """
    extractor = TicketmasterExtractor()
    return extractor.fetch_events(city=city, state=state)


if __name__ == "__main__":
    # Test the extractor
    events = extract_ticketmaster_events()
    print(f"\n📊 Total events extracted: {len(events)}")
    
    if events:
        print("\n🎫 Sample event:")
        print(f"Title: {events[0]['title']}")
        print(f"Date: {events[0]['start_at']}")
        print(f"Venue: {events[0]['venue']}")
        print(f"City: {events[0]['city']}")
        print(f"URL: {events[0]['source_url']}")

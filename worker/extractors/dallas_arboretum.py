"""
Dallas Arboretum & Botanical Garden Event Scraper
Extracts kids and family-friendly events from Dallas Arboretum
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional


class DallasArboretumExtractor:
    """Extract events from Dallas Arboretum & Botanical Garden"""
    
    def __init__(self):
        self.base_url = 'https://www.dallasarboretum.org'
        self.calendar_url = f'{self.base_url}/events-activities/calendar/'
        self.events_url = f'{self.base_url}/events-activities/'
        
        # Family-friendly keywords to prioritize
        self.family_keywords = [
            'kid', 'child', 'family', 'youth', 'junior', 'learning',
            'workshop', 'class', 'educational', 'santa', 'holiday',
            'craft', 'story', 'adventure', 'discovery', 'nature'
        ]
    
    def fetch_events(self) -> List[Dict]:
        """
        Fetch all events from Dallas Arboretum calendar
        
        Returns:
            List of event dictionaries
        """
        print(f"🌸 Fetching Dallas Arboretum events from calendar...")
        
        try:
            # Step 1: Get calendar page to find all event URLs
            event_urls = self._scrape_calendar_page()
            print(f"📅 Found {len(event_urls)} events in calendar")
            
            # Step 2: Fetch details for each event (limit to prevent overload)
            max_events = 50  # Reasonable limit
            events = []
            
            for i, url in enumerate(event_urls[:max_events], 1):
                print(f"   [{i}/{min(len(event_urls), max_events)}] Fetching: {url.split('/')[-2]}...")
                event_data = self._fetch_event_details(url)
                if event_data:
                    events.append(event_data)
            
            print(f"✅ Successfully parsed {len(events)} Dallas Arboretum events")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching Dallas Arboretum events: {e}")
            return []
    
    def _scrape_calendar_page(self) -> List[str]:
        """
        Scrape the calendar page to get all event URLs
        
        Returns:
            List of event detail page URLs
        """
        try:
            response = requests.get(
                self.calendar_url,
                timeout=30,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all "Learn More" links to event detail pages
            event_urls = set()  # Use set to avoid duplicates
            
            # Look for links containing /event/ in the href
            event_links = soup.find_all('a', href=lambda x: x and '/event/' in x)
            
            for link in event_links:
                href = link.get('href')
                # Make absolute URL if relative
                if href.startswith('/'):
                    href = self.base_url + href
                # Only add if it's an event detail page
                if '/event/' in href and href not in event_urls:
                    event_urls.add(href)
            
            return list(event_urls)
            
        except Exception as e:
            print(f"⚠️  Error scraping calendar: {e}")
            return []
    
    def _fetch_event_details(self, url: str) -> Optional[Dict]:
        """
        Fetch full event details from an individual event page
        
        Args:
            url: Event detail page URL
            
        Returns:
            Parsed event dictionary or None
        """
        try:
            response = requests.get(
                url,
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find JSON-LD data (most reliable)
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
                            return self._parse_event(item)
                
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            print(f"      ⚠️  Error fetching {url}: {str(e)[:50]}")
            return None
    
    def _parse_event(self, data: Dict) -> Optional[Dict]:
        """Parse a single JSON-LD Event object from Dallas Arboretum"""
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
                try:
                    end_at = date_parser.parse(data['endDate'])
                except:
                    pass
            
            # Extract location
            location = data.get('location', {})
            venue = "Dallas Arboretum & Botanical Garden"
            address = "8525 Garland Road"
            city = "Dallas"
            
            # Override with specific location if provided
            if isinstance(location, dict):
                venue_name = location.get('name')
                if venue_name and venue_name != "Dallas Arboretum: ":
                    # Append specific location to main venue
                    venue = f"{venue} - {venue_name}"
                
                address_data = location.get('address', {})
                if isinstance(address_data, dict):
                    street = address_data.get('streetAddress')
                    if street:
                        address = street
                    locality = address_data.get('addressLocality')
                    if locality:
                        city = locality
            
            # Extract price - Dallas Arboretum has general admission
            price_tier = "PAID"
            price_amount = None
            
            offers = data.get('offers', {})
            if isinstance(offers, dict):
                price = offers.get('price')
                if price:
                    try:
                        price_float = float(price)
                        if price_float == 0:
                            price_tier = "FREE"
                        else:
                            price_amount = str(price_float)
                    except:
                        pass
            
            # Most Dallas Arboretum events require general admission
            # Set a note in description if no specific price
            if not price_amount and price_tier == "PAID":
                price_amount = "17"  # General admission for adults
            
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
            description = data.get('description', '')
            
            # Add admission note if not free
            if price_tier == "PAID" and description:
                if "admission" not in description.lower():
                    description = f"{description}\n\nGeneral admission to Dallas Arboretum applies."
            
            # Extract event URL
            event_url = data.get('url', self.events_url)
            
            # Determine if family-friendly
            is_family_friendly = self._is_family_friendly(title, description)
            
            # Category detection
            category = self._determine_category(title, description)
            
            # Build event dictionary
            parsed_event = {
                'title': title,
                'description': description,
                'start_at': start_at.isoformat(),
                'end_at': end_at.isoformat() if end_at else None,
                'venue': venue,
                'address': address,
                'city': city,
                'price_tier': price_tier,
                'price_amount': price_amount,
                'image_url': image_url,
                'source_url': event_url,
                'source_type': 'DALLAS_ARBORETUM',
                'category': category,
                'is_family_friendly': is_family_friendly,
                'organizer': 'Dallas Arboretum & Botanical Garden'
            }
            
            return parsed_event
            
        except Exception as e:
            print(f"⚠️  Error parsing Dallas Arboretum event: {e}")
            return None
    
    def _is_family_friendly(self, title: str, description: str) -> bool:
        """Determine if event is family-friendly based on keywords"""
        text = f"{title} {description}".lower()
        
        for keyword in self.family_keywords:
            if keyword in text:
                return True
        
        return False
    
    def _determine_category(self, title: str, description: str) -> str:
        """Determine event category"""
        text = f"{title} {description}".lower()
        
        # Category keywords
        if any(word in text for word in ['tea', 'dinner', 'lunch', 'brunch', 'food']):
            return 'Food & Dining'
        elif any(word in text for word in ['concert', 'music', 'performance']):
            return 'Music'
        elif any(word in text for word in ['class', 'workshop', 'learning', 'education']):
            return 'Education'
        elif any(word in text for word in ['holiday', 'christmas', 'santa', 'halloween', 'easter']):
            return 'Holiday'
        elif any(word in text for word in ['garden', 'plant', 'flower', 'nature', 'outdoor']):
            return 'Nature & Gardens'
        else:
            return 'Family & Kids'


def extract_dallas_arboretum_events() -> List[Dict]:
    """
    Main function to extract Dallas Arboretum events
    
    Returns:
        List of parsed events
    """
    extractor = DallasArboretumExtractor()
    return extractor.fetch_events()


if __name__ == "__main__":
    # Test the extractor
    events = extract_dallas_arboretum_events()
    print(f"\n📊 Total events extracted: {len(events)}")
    
    # Count family-friendly events
    family_events = [e for e in events if e.get('is_family_friendly')]
    print(f"👨‍👩‍👧‍👦 Family-friendly events: {len(family_events)}")
    
    if events:
        print("\n🌸 Sample event:")
        print(f"Title: {events[0]['title']}")
        print(f"Date: {events[0]['start_at']}")
        print(f"Venue: {events[0]['venue']}")
        print(f"Category: {events[0]['category']}")
        print(f"Family-friendly: {events[0]['is_family_friendly']}")
        print(f"URL: {events[0]['source_url']}")

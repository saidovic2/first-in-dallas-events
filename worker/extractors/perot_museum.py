"""
Perot Museum of Nature and Science Event Scraper
Extracts educational and family-friendly events
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional
import re


class PerotMuseumExtractor:
    """Extract events from Perot Museum of Nature and Science"""
    
    def __init__(self):
        self.base_url = 'https://www.perotmuseum.org'
        self.events_url = f'{self.base_url}/events'
    
    def fetch_events(self) -> List[Dict]:
        """
        Fetch all events from Perot Museum
        
        Returns:
            List of event dictionaries
        """
        print(f"🔬 Fetching Perot Museum events...")
        
        try:
            response = requests.get(
                self.events_url,
                timeout=30,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all event links on the page
            event_urls = self._extract_event_urls(soup)
            print(f"📅 Found {len(event_urls)} potential events")
            
            # Fetch details for each event
            events = []
            for i, url in enumerate(event_urls[:30], 1):  # Limit to 30
                print(f"   [{i}/{min(len(event_urls), 30)}] Fetching: {url.split('/')[-1][:40]}...")
                event_data = self._fetch_event_details(url)
                if event_data:
                    events.append(event_data)
            
            print(f"✅ Successfully parsed {len(events)} Perot Museum events")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching Perot Museum events: {e}")
            return []
    
    def _extract_event_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract event URLs from the main events page"""
        event_urls = set()
        
        # Look for links to event pages - be more specific
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            # Only get actual event detail pages, not category pages
            if href and '/events/' in href:
                # Skip navigation/category pages
                if any(skip in href.lower() for skip in ['/events/adults', '/events/families', '/events/educators', '/events/teens', '/events?', 'category=', 'filter=']):
                    continue
                    
                if href.startswith('/'):
                    href = self.base_url + href
                elif not href.startswith('http'):
                    continue
                    
                # Only add if it looks like a real event detail page
                if href != self.events_url and href != self.base_url + '/events':
                    event_urls.add(href)
        
        return list(event_urls)
    
    def _fetch_event_details(self, url: str) -> Optional[Dict]:
        """Fetch full event details from an individual event page"""
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try JSON-LD first
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    items = data if isinstance(data, list) else [data]
                    
                    for item in items:
                        if item.get('@type') == 'Event':
                            return self._parse_json_ld_event(item, url)
                except:
                    continue
            
            # Fallback to HTML parsing
            return self._parse_html_event(soup, url)
            
        except Exception as e:
            print(f"      ⚠️  Error: {str(e)[:50]}")
            return None
    
    def _parse_json_ld_event(self, data: Dict, url: str) -> Optional[Dict]:
        """Parse event from JSON-LD data"""
        try:
            title = data.get('name')
            start_date = data.get('startDate')
            
            if not title or not start_date:
                print(f"      ⚠️  Missing required fields (title or date)")
                return None
            
            description = data.get('description', '')
            
            # Parse dates
            start_at = date_parser.parse(start_date)
            
            # Skip past events - keep today and future events
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            # Compare dates only (not time) - keep today's events
            if start_at.date() < now.date():
                print(f"      ⏭️  Skipping past event (date: {start_at.date()})")
                return None
            
            end_at = None
            if data.get('endDate'):
                try:
                    end_at = date_parser.parse(data.get('endDate'))
                except:
                    pass
            
            # Location
            location = data.get('location', {})
            venue = location.get('name', 'Perot Museum of Nature and Science')
            address = location.get('address', {})
            if isinstance(address, dict):
                address = address.get('streetAddress', '2201 N Field St')
            else:
                address = '2201 N Field St'
            
            # Price
            offers = data.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            
            price_text = offers.get('price', '')
            if price_text and (price_text == '0' or price_text.lower() == 'free'):
                price_tier = 'FREE'
                price_amount = None
            else:
                price_tier = 'PAID'
                try:
                    price_amount = float(re.sub(r'[^\d.]', '', str(price_text))) if price_text else None
                except:
                    price_amount = None
            
            # Image
            image_url = data.get('image')
            if isinstance(image_url, list):
                image_url = image_url[0] if image_url else None
            if image_url and image_url.startswith('/'):
                image_url = self.base_url + image_url
            
            return {
                'title': title,
                'description': description[:500] if description else None,
                'start_at': start_at.isoformat(),
                'end_at': end_at.isoformat() if end_at else None,
                'venue': venue,
                'address': address,
                'city': 'Dallas',
                'price_tier': price_tier,
                'price_amount': price_amount,
                'image_url': image_url,
                'source_url': url,
                'source_type': 'PEROT_MUSEUM',
                'category': 'Education & Science',
                'is_family_friendly': True,  # Perot Museum is inherently family-friendly
                'organizer': 'Perot Museum of Nature and Science'
            }
        except Exception as e:
            print(f"      ⚠️  Parse error: {str(e)[:50]}")
            return None
    
    def _parse_html_event(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Parse event from HTML when JSON-LD is not available"""
        try:
            # Get title
            title_elem = soup.find('h1')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Get description
            description = ''
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # Try to find date information
            # This is a fallback - may need adjustment based on actual HTML structure
            date_text = soup.get_text()
            
            # Look for date patterns
            import re
            date_pattern = r'([A-Za-z]+\s+\d{1,2},\s+\d{4})'
            date_match = re.search(date_pattern, date_text)
            
            if not date_match:
                print(f"      ⚠️  No date found in HTML")
                return None  # Skip if no date found
            
            start_at = date_parser.parse(date_match.group(1))
            
            # Get image
            image_url = None
            meta_image = soup.find('meta', property='og:image')
            if meta_image:
                image_url = meta_image.get('content')
                if image_url and image_url.startswith('/'):
                    image_url = self.base_url + image_url
            
            return {
                'title': title,
                'description': description[:500] if description else None,
                'start_at': start_at.isoformat(),
                'end_at': None,
                'venue': 'Perot Museum of Nature and Science',
                'address': '2201 N Field St',
                'city': 'Dallas',
                'price_tier': 'PAID',  # Default to PAID for museum events
                'price_amount': None,
                'image_url': image_url,
                'source_url': url,
                'source_type': 'PEROT_MUSEUM',
                'category': 'Education & Science',
                'is_family_friendly': True,
                'organizer': 'Perot Museum of Nature and Science'
            }
        except Exception as e:
            print(f"      ⚠️  HTML parse error: {str(e)[:50]}")
            return None


def extract_perot_museum_events() -> List[Dict]:
    """Main function to extract Perot Museum events"""
    extractor = PerotMuseumExtractor()
    return extractor.fetch_events()


# For testing
if __name__ == "__main__":
    events = extract_perot_museum_events()
    print(f"\n📊 Extracted {len(events)} events")
    if events:
        print(f"\n📝 Sample Event:")
        print(json.dumps(events[0], indent=2, default=str))

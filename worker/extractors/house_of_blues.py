"""
House of Blues Dallas Event Scraper
Extracts music and entertainment events
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional
import re


class HouseOfBluesExtractor:
    """Extract events from House of Blues Dallas"""
    
    def __init__(self):
        self.base_url = 'https://www.houseofblues.com'
        self.events_url = f'{self.base_url}/dallas/events'
    
    def fetch_events(self) -> List[Dict]:
        """
        Fetch all events from House of Blues Dallas
        
        Returns:
            List of event dictionaries
        """
        print(f"🎸 Fetching House of Blues Dallas events...")
        
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
            
            # Find all event links
            event_urls = self._extract_event_urls(soup)
            print(f"📅 Found {len(event_urls)} events")
            
            # Fetch details for each event
            events = []
            for i, url in enumerate(event_urls[:50], 1):  # Limit to 50
                print(f"   [{i}/{min(len(event_urls), 50)}] Fetching: {url.split('/')[-1][:40]}...")
                event_data = self._fetch_event_details(url)
                if event_data:
                    events.append(event_data)
            
            print(f"✅ Successfully parsed {len(events)} House of Blues events")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching House of Blues events: {e}")
            return []
    
    def _extract_event_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract event URLs from the events listing page"""
        event_urls = set()
        
        print(f"      🔍 Scanning page for event links...")
        print(f"      📄 Page title: {soup.find('title').get_text() if soup.find('title') else 'No title'}")
        
        # Look for event links
        all_links = soup.find_all('a', href=True)
        print(f"      🔗 Found {len(all_links)} total links on page")
        
        # Sample first 10 links to see what we're dealing with
        for i, link in enumerate(all_links[:10]):
            href = link.get('href', '')
            print(f"         [{i+1}] {href[:80]}")
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/dallas/events/' in href and '/dallas/events' != href:
                if href.startswith('/'):
                    href = self.base_url + href
                elif not href.startswith('http'):
                    continue
                event_urls.add(href)
                print(f"      ✅ Matched event URL: {href}")
        
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
                        if item.get('@type') == 'MusicEvent' or item.get('@type') == 'Event':
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
                return None
            
            description = data.get('description', '')
            
            # Parse dates
            start_at = date_parser.parse(start_date)
            
            # Skip past events - keep today and future events
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
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
            venue = location.get('name', 'House of Blues Dallas')
            
            # Price
            offers = data.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            
            price_tier = 'PAID'
            price_amount = None
            
            if offers:
                price = offers.get('price')
                if price and price != '0':
                    try:
                        price_amount = float(price)
                        if price_amount > 100:
                            price_tier = 'PREMIUM'
                    except:
                        pass
            
            # Image
            image_url = data.get('image')
            if isinstance(image_url, list):
                image_url = image_url[0]
            if isinstance(image_url, dict):
                image_url = image_url.get('url')
            
            return {
                'title': title,
                'description': description[:500] if description else None,
                'start_at': start_at.isoformat(),
                'end_at': end_at.isoformat() if end_at else None,
                'venue': venue,
                'address': '2200 N Lamar St, Dallas, TX 75202',
                'city': 'Dallas',
                'price_tier': price_tier,
                'price_amount': price_amount,
                'image_url': image_url,
                'source_url': url,
                'category': 'Music & Performance',
                'is_family_friendly': False  # Music venue, typically 18+
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
            
            # Get date from page
            date_elem = soup.find('time') or soup.find(class_=re.compile('date|time'))
            if not date_elem:
                return None
            
            date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
            start_at = date_parser.parse(date_text)
            
            # Skip past events
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            if start_at.date() < now.date():
                print(f"      ⏭️  Skipping past event (date: {start_at.date()})")
                return None
            
            # Get image
            image_url = None
            meta_image = soup.find('meta', property='og:image')
            if meta_image:
                image_url = meta_image.get('content')
            
            return {
                'title': title,
                'description': description[:500] if description else None,
                'start_at': start_at.isoformat(),
                'end_at': None,
                'venue': 'House of Blues Dallas',
                'address': '2200 N Lamar St, Dallas, TX 75202',
                'city': 'Dallas',
                'price_tier': 'PAID',
                'price_amount': None,
                'image_url': image_url,
                'source_url': url,
                'category': 'Music & Performance',
                'is_family_friendly': False
            }
            
        except Exception as e:
            print(f"      ⚠️  Parse error: {str(e)[:50]}")
            return None


def extract_house_of_blues_events():
    """Helper function for worker.py"""
    extractor = HouseOfBluesExtractor()
    return extractor.fetch_events()

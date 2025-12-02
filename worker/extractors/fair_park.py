"""
Fair Park Dallas Event Scraper
Extracts cultural festivals, concerts, and community events
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional
import re


class FairParkExtractor:
    """Extract events from Fair Park Dallas"""
    
    def __init__(self):
        self.base_url = 'https://www.fairparkdallas.com'
        self.events_url = f'{self.base_url}/events'
    
    def fetch_events(self) -> List[Dict]:
        """
        Fetch all events from Fair Park Dallas
        
        Returns:
            List of event dictionaries
        """
        print(f"🎡 Fetching Fair Park events...")
        
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
            for i, url in enumerate(event_urls[:40], 1):  # Limit to 40
                print(f"   [{i}/{min(len(event_urls), 40)}] Fetching: {url.split('/')[-1][:40]}...")
                event_data = self._fetch_event_details(url)
                if event_data:
                    events.append(event_data)
            
            print(f"✅ Successfully parsed {len(events)} Fair Park events")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching Fair Park events: {e}")
            return []
    
    def _extract_event_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract event URLs from the events page"""
        event_urls = set()
        
        # Look for event detail links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and ('/events/detail/' in href or '/event/' in href):
                if href.startswith('/'):
                    href = self.base_url + href
                elif not href.startswith('http'):
                    continue
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
                return None
            
            description = data.get('description', '')
            
            # Parse dates
            start_at = date_parser.parse(start_date)
            
            # Skip past events - only get upcoming events
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            if start_at < now:
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
            venue = location.get('name', 'Fair Park')
            
            # Price
            offers = data.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            
            price_text = offers.get('price', '')
            if price_text and (str(price_text) == '0' or str(price_text).lower() == 'free'):
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
            
            # Categorize
            category = self._categorize_event(title, description)
            is_family_friendly = self._is_family_friendly(title, description)
            
            return {
                'title': title,
                'description': description[:500] if description else None,
                'start_at': start_at.isoformat(),
                'end_at': end_at.isoformat() if end_at else None,
                'venue': venue,
                'address': '1121 1st Ave',
                'city': 'Dallas',
                'price_tier': price_tier,
                'price_amount': price_amount,
                'image_url': image_url,
                'source_url': url,
                'source_type': 'FAIR_PARK',
                'category': category,
                'is_family_friendly': is_family_friendly,
                'organizer': 'Fair Park'
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
            text = soup.get_text()
            
            # Look for date patterns
            date_pattern = r'([A-Za-z]+,?\s+[A-Za-z]+\s+\d{1,2},?\s+\d{4})'
            date_match = re.search(date_pattern, text)
            
            if not date_match:
                # Try alternate pattern
                date_pattern2 = r'(\d{1,2}/\d{1,2}/\d{4})'
                date_match = re.search(date_pattern2, text)
            
            if not date_match:
                return None  # Skip if no date found
            
            try:
                start_at = date_parser.parse(date_match.group(1))
                
                # Skip past events - only get upcoming events
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                if start_at < now:
                    print(f"      ⏭️  Skipping past event (date: {start_at.date()})")
                    return None
            except:
                return None
            
            # Get image
            image_url = None
            meta_image = soup.find('meta', property='og:image')
            if meta_image:
                image_url = meta_image.get('content')
                if image_url and image_url.startswith('/'):
                    image_url = self.base_url + image_url
            
            # Categorize
            category = self._categorize_event(title, description)
            is_family_friendly = self._is_family_friendly(title, description)
            
            return {
                'title': title,
                'description': description[:500] if description else None,
                'start_at': start_at.isoformat(),
                'end_at': None,
                'venue': 'Fair Park',
                'address': '1121 1st Ave',
                'city': 'Dallas',
                'price_tier': 'PAID',  # Default to paid
                'price_amount': None,
                'image_url': image_url,
                'source_url': url,
                'source_type': 'FAIR_PARK',
                'category': category,
                'is_family_friendly': is_family_friendly,
                'organizer': 'Fair Park'
            }
        except Exception as e:
            print(f"      ⚠️  HTML parse error: {str(e)[:50]}")
            return None
    
    def _is_family_friendly(self, title: str, description: str) -> bool:
        """Determine if event is family-friendly"""
        text = f"{title} {description}".lower()
        
        # Family-friendly indicators
        family_keywords = [
            'family', 'kid', 'child', 'youth', 'festival', 'fair',
            'community', 'cultural', 'holiday', 'celebration'
        ]
        
        # Adult-only indicators
        adult_keywords = ['21+', 'adult only', 'adults only', 'bar crawl', 'nightclub']
        
        for keyword in adult_keywords:
            if keyword in text:
                return False
        
        for keyword in family_keywords:
            if keyword in text:
                return True
        
        # Default to family-friendly for Fair Park (it's a public park/venue)
        return True
    
    def _categorize_event(self, title: str, description: str) -> str:
        """Categorize event based on content"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['concert', 'music', 'band', 'orchestra']):
            return 'Music & Concerts'
        elif any(word in text for word in ['festival', 'fair', 'celebration']):
            return 'Festivals & Fairs'
        elif any(word in text for word in ['cultural', 'heritage', 'tradition']):
            return 'Cultural Events'
        elif any(word in text for word in ['sport', 'game', 'match', 'soccer', 'football']):
            return 'Sports & Recreation'
        elif any(word in text for word in ['food', 'culinary', 'taste']):
            return 'Food & Dining'
        elif any(word in text for word in ['art', 'exhibit', 'gallery']):
            return 'Arts & Culture'
        elif any(word in text for word in ['family', 'kid', 'children']):
            return 'Family & Kids'
        else:
            return 'Community Events'


def extract_fair_park_events() -> List[Dict]:
    """Main function to extract Fair Park events"""
    extractor = FairParkExtractor()
    return extractor.fetch_events()


# For testing
if __name__ == "__main__":
    events = extract_fair_park_events()
    print(f"\n📊 Extracted {len(events)} events")
    if events:
        print(f"\n📝 Sample Event:")
        print(json.dumps(events[0], indent=2, default=str))

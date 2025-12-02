"""
Dallas Zoo Event Scraper
Extracts animal and nature-focused family events
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional
import re


class DallasZooExtractor:
    """Extract events from Dallas Zoo"""
    
    def __init__(self):
        self.base_url = 'https://www.dallaszoo.com'
        self.events_url = f'{self.base_url}/events'
    
    def fetch_events(self) -> List[Dict]:
        """
        Fetch all events from Dallas Zoo
        
        Returns:
            List of event dictionaries
        """
        print(f"🦁 Fetching Dallas Zoo events...")
        
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
            for i, url in enumerate(event_urls[:30], 1):  # Limit to 30
                print(f"   [{i}/{min(len(event_urls), 30)}] Fetching: {url.split('/')[-1][:40]}...")
                event_data = self._fetch_event_details(url)
                if event_data:
                    events.append(event_data)
            
            print(f"✅ Successfully parsed {len(events)} Dallas Zoo events")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching Dallas Zoo events: {e}")
            return []
    
    def _extract_event_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract event URLs from the events page"""
        event_urls = set()
        
        # Look for event links - typically in event cards or listings
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            # Zoo event pages often contain specific keywords
            if href and any(keyword in href for keyword in ['/event/', '/events/', '-nights', '-days', '-lights']):
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
            print(f"      🔍 Found {len(json_ld_scripts)} JSON-LD scripts")
            
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    items = data if isinstance(data, list) else [data]
                    
                    for item in items:
                        if item.get('@type') == 'Event':
                            print(f"      📋 Found Event in JSON-LD")
                            return self._parse_json_ld_event(item, url)
                except Exception as e:
                    print(f"      ⚠️  JSON-LD parse error: {str(e)[:40]}")
                    continue
            
            # Fallback to HTML parsing
            print(f"      📄 No JSON-LD found, trying HTML parsing...")
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
                print(f"      ⚠️  Missing title or date (title={title}, date={start_date})")
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
            venue = location.get('name', 'Dallas Zoo')
            
            # Price
            offers = data.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            
            price_text = offers.get('price', '')
            if price_text and (str(price_text) == '0' or str(price_text).lower() == 'free'):
                price_tier = 'FREE'
                price_amount = None
            elif price_text and str(price_text) == '1':
                price_tier = 'PAID'
                price_amount = 1.0
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
                'address': '650 S R L Thornton Fwy',
                'city': 'Dallas',
                'price_tier': price_tier,
                'price_amount': price_amount,
                'image_url': image_url,
                'source_url': url,
                'source_type': 'DALLAS_ZOO',
                'category': 'Animals & Nature',
                'is_family_friendly': self._is_family_friendly(title, description),
                'organizer': 'Dallas Zoo'
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
                print(f"      ⚠️  No H1 title found in HTML")
                return None
            title = title_elem.get_text(strip=True)
            print(f"      📌 Title: {title[:50]}")
            
            # Get description
            description = ''
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # For Dallas Zoo, many events are recurring/seasonal
            # Try to extract date info from page
            text = soup.get_text()
            
            # Look for date patterns (multiple formats)
            date_patterns = [
                r'([A-Za-z]+\s+\d{1,2},\s+\d{4})',  # "November 15, 2025"
                r'(\d{1,2}/\d{1,2}/\d{4})',  # "11/15/2025"
                r'([A-Za-z]+\s+\d{1,2}-\d{1,2},\s+\d{4})',  # "November 15-20, 2025"
                r'([A-Za-z]+\s+\d{4})',  # "November 2025"
            ]
            
            date_match = None
            for pattern in date_patterns:
                date_match = re.search(pattern, text)
                if date_match:
                    print(f"      🔍 Matched pattern: {pattern[:30]}")
                    break
            
            # If no specific date, check for season/timeframe
            season_pattern = r'(summer|fall|winter|spring|holiday)\s+(\d{4})'
            season_match = re.search(season_pattern, text, re.IGNORECASE) if not date_match else None
            
            if date_match:
                start_at = date_parser.parse(date_match.group(1))
                print(f"      📅 Found date: {date_match.group(1)}")
            elif season_match:
                # Use current year and season start
                season = season_match.group(1).lower()
                year = int(season_match.group(2))
                season_dates = {
                    'spring': f'March 1, {year}',
                    'summer': f'June 1, {year}',
                    'fall': f'September 1, {year}',
                    'winter': f'December 1, {year}',
                    'holiday': f'December 1, {year}'
                }
                start_at = date_parser.parse(season_dates.get(season, f'January 1, {year}'))
                print(f"      📅 Found seasonal date: {season} {year}")
            else:
                # If no date found, assume it's a current/ongoing event
                # Use today's date as start
                from datetime import datetime, timezone
                start_at = datetime.now(timezone.utc)
                print(f"      ℹ️  No specific date found - using today as start date")
            
            # Skip past events - keep today and future events
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            # Compare dates only (not time) - keep today's events
            if start_at.date() < now.date():
                print(f"      ⏭️  Skipping past event (date: {start_at.date()})")
                return None
            
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
                'venue': 'Dallas Zoo',
                'address': '650 S R L Thornton Fwy',
                'city': 'Dallas',
                'price_tier': 'PAID',  # Zoo admission required
                'price_amount': None,
                'image_url': image_url,
                'source_url': url,
                'source_type': 'DALLAS_ZOO',
                'category': 'Animals & Nature',
                'is_family_friendly': True,  # Most zoo events are family-friendly
                'organizer': 'Dallas Zoo'
            }
        except Exception as e:
            print(f"      ⚠️  HTML parse error: {str(e)[:50]}")
            return None
    
    def _is_family_friendly(self, title: str, description: str) -> bool:
        """Determine if event is family-friendly"""
        text = f"{title} {description}".lower()
        
        # Adult-only keywords
        adult_keywords = ['adult only', 'adults only', '21+', 'after dark', 'zoo to do']
        
        for keyword in adult_keywords:
            if keyword in text:
                return False
        
        # Most zoo events are family-friendly
        return True


def extract_dallas_zoo_events() -> List[Dict]:
    """Main function to extract Dallas Zoo events"""
    extractor = DallasZooExtractor()
    return extractor.fetch_events()


# For testing
if __name__ == "__main__":
    events = extract_dallas_zoo_events()
    print(f"\n📊 Extracted {len(events)} events")
    if events:
        print(f"\n📝 Sample Event:")
        print(json.dumps(events[0], indent=2, default=str))

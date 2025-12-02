"""
Klyde Warren Park Event Scraper
Extracts family-friendly events from Klyde Warren Park
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional
import re


class KlydeWarrenParkExtractor:
    """Extract events from Klyde Warren Park"""
    
    def __init__(self):
        self.base_url = 'https://www.klydewarrenpark.org'
        self.events_url = f'{self.base_url}/events-programming'
        
        # Family-friendly keywords (most Klyde Warren events are family-friendly!)
        self.family_keywords = [
            'kid', 'child', 'family', 'youth', 'junior', 'learning',
            'workshop', 'class', 'educational', 'santa', 'holiday',
            'craft', 'story', 'movie', 'music', 'dog', 'pet', 'play',
            'adventure', 'discovery', 'nature', 'art', 'painting'
        ]
    
    def fetch_events(self) -> List[Dict]:
        """
        Fetch all events from Klyde Warren Park
        
        Returns:
            List of event dictionaries
        """
        print(f"🌳 Fetching Klyde Warren Park events...")
        
        try:
            # Step 1: Get events listing page to find all event URLs
            event_urls = self._scrape_events_page()
            print(f"📅 Found {len(event_urls)} events")
            
            # Step 2: Fetch details for each event (limit to prevent overload)
            max_events = 50  # Reasonable limit
            events = []
            
            for i, url in enumerate(event_urls[:max_events], 1):
                print(f"   [{i}/{min(len(event_urls), max_events)}] Fetching: {url.split('/')[-1][:40]}...")
                event_data = self._fetch_event_details(url)
                if event_data:
                    events.append(event_data)
            
            print(f"✅ Successfully parsed {len(events)} Klyde Warren Park events")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching Klyde Warren Park events: {e}")
            return []
    
    def _scrape_events_page(self) -> List[str]:
        """
        Scrape the events page to get all event URLs
        
        Returns:
            List of event detail page URLs
        """
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
            event_urls = set()  # Use set to avoid duplicates
            
            # Look for links containing /events-programming/ in the href
            event_links = soup.find_all('a', href=lambda x: x and '/events-programming/' in x and x != '/events-programming')
            
            for link in event_links:
                href = link.get('href')
                # Make absolute URL if relative
                if href.startswith('/'):
                    href = self.base_url + href
                # Only add if it's an event detail page (not the main listing)
                if '/events-programming/' in href and href != self.events_url:
                    # Remove query parameters and fragments
                    href = href.split('?')[0].split('#')[0]
                    event_urls.add(href)
            
            return list(event_urls)
            
        except Exception as e:
            print(f"⚠️  Error scraping events page: {e}")
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
            
            # Try to parse from structured data first
            event_data = self._parse_from_html(soup, url)
            
            return event_data
            
        except Exception as e:
            print(f"      ⚠️  Error fetching {url}: {str(e)[:50]}")
            return None
    
    def _parse_from_html(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """
        Parse event details from HTML
        
        Args:
            soup: BeautifulSoup object
            url: Event URL
            
        Returns:
            Parsed event dictionary or None
        """
        try:
            # Get title from h1
            title_elem = soup.find('h1')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Get description from meta tag or first paragraph
            description = ''
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                description = meta_desc.get('content', '')
            
            if not description:
                # Try to find description in the page content
                paragraphs = soup.find_all('p')
                if paragraphs:
                    description = ' '.join([p.get_text(strip=True) for p in paragraphs[:2]])
            
            # Find date and time information
            # Look for text patterns like "Saturday, December 6, 2025"
            date_text = None
            time_start = None
            time_end = None
            
            # Search for date patterns in the page
            text_content = soup.get_text()
            
            # Pattern: "Saturday, December 6, 2025"
            date_pattern = r'([A-Za-z]+,\s+[A-Za-z]+\s+\d{1,2},\s+\d{4})'
            date_match = re.search(date_pattern, text_content)
            if date_match:
                date_text = date_match.group(1)
            
            # Pattern: "4:00 PM" or "4:00 PM - 8:30 PM"
            time_pattern = r'(\d{1,2}:\d{2}\s*[AP]M)'
            time_matches = re.findall(time_pattern, text_content)
            if time_matches:
                time_start = time_matches[0] if len(time_matches) >= 1 else None
                time_end = time_matches[1] if len(time_matches) >= 2 else None
            
            # Parse dates
            if not date_text:
                print(f"      ⚠️  No date found for {title}")
                return None
            
            # Combine date and time
            start_datetime_str = date_text
            if time_start:
                start_datetime_str += f" {time_start}"
            
            try:
                start_at = date_parser.parse(start_datetime_str)
            except:
                print(f"      ⚠️  Could not parse date: {start_datetime_str}")
                return None
            
            # Parse end time if available
            end_at = None
            if time_end:
                end_datetime_str = date_text + f" {time_end}"
                try:
                    end_at = date_parser.parse(end_datetime_str)
                except:
                    pass
            
            # Venue and location
            venue = "Klyde Warren Park"
            address = "2012 Woodall Rodgers Freeway"
            city = "Dallas"
            
            # Price - Klyde Warren Park events are FREE!
            price_tier = "FREE"
            price_amount = None
            
            # Get image - look for og:image meta tag
            image_url = None
            meta_image = soup.find('meta', property='og:image')
            if meta_image:
                image_url = meta_image.get('content')
                # Make absolute URL if needed
                if image_url and image_url.startswith('/'):
                    image_url = self.base_url + image_url
            
            # Detect if family-friendly (most Klyde Warren events are!)
            is_family_friendly = self._is_family_friendly(title, description)
            
            # Categorize event
            category = self._categorize_event(title, description)
            
            # Build event object
            parsed_event = {
                'title': title,
                'description': description[:500] if description else None,  # Limit description length
                'start_at': start_at.isoformat(),
                'end_at': end_at.isoformat() if end_at else None,
                'venue': venue,
                'address': address,
                'city': city,
                'price_tier': price_tier,
                'price_amount': price_amount,
                'image_url': image_url,
                'source_url': url,
                'source_type': 'KLYDE_WARREN_PARK',
                'category': category,
                'is_family_friendly': is_family_friendly,
                'organizer': 'Klyde Warren Park'
            }
            
            return parsed_event
            
        except Exception as e:
            print(f"      ⚠️  Error parsing event: {str(e)[:50]}")
            return None
    
    def _is_family_friendly(self, title: str, description: str) -> bool:
        """Check if event is family-friendly based on keywords"""
        text = f"{title} {description}".lower()
        
        # Klyde Warren Park is generally very family-friendly
        # Default to True unless it's clearly an adult-only event
        adult_keywords = ['wine', 'beer', '21+', 'adults only', 'cocktail', 'bar']
        
        for keyword in adult_keywords:
            if keyword in text:
                return False
        
        # Otherwise assume family-friendly (Klyde Warren is a family park!)
        return True
    
    def _categorize_event(self, title: str, description: str) -> str:
        """Categorize event based on content"""
        text = f"{title} {description}".lower()
        
        # Category mapping
        if any(word in text for word in ['concert', 'music', 'band', 'dj', 'performance', 'singer']):
            return 'Music & Concerts'
        elif any(word in text for word in ['movie', 'film', 'screening']):
            return 'Movies & Film'
        elif any(word in text for word in ['food', 'chef', 'cooking', 'culinary', 'restaurant']):
            return 'Food & Dining'
        elif any(word in text for word in ['art', 'paint', 'craft', 'draw', 'creative']):
            return 'Arts & Theatre'
        elif any(word in text for word in ['kid', 'child', 'family', 'story time', 'children']):
            return 'Family & Kids'
        elif any(word in text for word in ['fitness', 'yoga', 'workout', 'exercise', 'health']):
            return 'Health & Fitness'
        elif any(word in text for word in ['dog', 'pet', 'paws', 'puppy', 'adoption']):
            return 'Animals & Pets'
        elif any(word in text for word in ['holiday', 'christmas', 'halloween', 'thanksgiving', 'easter']):
            return 'Holiday Events'
        else:
            return 'Other'


def extract_klyde_warren_park_events() -> List[Dict]:
    """
    Main function to extract Klyde Warren Park events
    
    Returns:
        List of event dictionaries
    """
    extractor = KlydeWarrenParkExtractor()
    return extractor.fetch_events()


# For testing
if __name__ == "__main__":
    events = extract_klyde_warren_park_events()
    print(f"\n📊 Extracted {len(events)} events")
    if events:
        print(f"\n📝 Sample Event:")
        print(json.dumps(events[0], indent=2, default=str))

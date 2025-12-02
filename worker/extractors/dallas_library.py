"""
Dallas Public Library Event Scraper
Extracts FREE educational and family-friendly events
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from typing import List, Dict, Optional
import re


class DallasLibraryExtractor:
    """Extract events from Dallas Public Library"""
    
    def __init__(self):
        self.base_url = 'https://dallaslibrary.librarymarket.com'
        self.events_url = f'{self.base_url}/events/upcoming'
    
    def fetch_events(self) -> List[Dict]:
        """
        Fetch all events from Dallas Public Library
        
        Returns:
            List of event dictionaries
        """
        print(f"📚 Fetching Dallas Public Library events...")
        
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
            
            # Fetch details for each event (limit to prevent overload)
            max_events = 50  # Libraries have LOTS of events
            events = []
            
            for i, url in enumerate(event_urls[:max_events], 1):
                print(f"   [{i}/{min(len(event_urls), max_events)}] Fetching: {url.split('/')[-1][:40]}...")
                event_data = self._fetch_event_details(url)
                if event_data:
                    events.append(event_data)
            
            print(f"✅ Successfully parsed {len(events)} Dallas Public Library events")
            return events
            
        except Exception as e:
            print(f"❌ Error fetching Dallas Public Library events: {e}")
            return []
    
    def _extract_event_urls(self, soup: BeautifulSoup) -> List[str]:
        """Extract event URLs from the events listing page"""
        event_urls = set()
        
        # Look for event links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and '/event/' in href:
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
            return self._parse_event(soup, url)
            
        except Exception as e:
            print(f"      ⚠️  Error: {str(e)[:50]}")
            return None
    
    def _parse_event(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        """Parse event details from HTML"""
        try:
            # Get title
            title_elem = soup.find('h1') or soup.find('h2', class_='event-title')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)
            
            # Get description
            description = ''
            desc_elem = soup.find('div', class_='field-name-body') or soup.find('div', class_='event-description')
            if desc_elem:
                description = desc_elem.get_text(strip=True)
            
            # Meta description fallback
            if not description:
                meta_desc = soup.find('meta', property='og:description')
                if meta_desc:
                    description = meta_desc.get('content', '')
            
            # Get date/time information
            # Library events often have date in a specific div
            date_elem = soup.find('span', class_='date-display-single') or soup.find('time')
            
            if not date_elem:
                # Try to find date in page text
                text = soup.get_text()
                date_pattern = r'([A-Za-z]+,\s+[A-Za-z]+\s+\d{1,2},\s+\d{4})'
                date_match = re.search(date_pattern, text)
                if not date_match:
                    return None
                date_text = date_match.group(1)
            else:
                date_text = date_elem.get_text(strip=True)
            
            # Parse date
            try:
                start_at = date_parser.parse(date_text)
                
                # Skip past events - only get upcoming events
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                if start_at < now:
                    print(f"      ⏭️  Skipping past event (date: {start_at.date()})")
                    return None
            except:
                return None
            
            # Get venue/location - Library branch name
            venue = 'Dallas Public Library'
            location_elem = soup.find('div', class_='location-name') or soup.find('span', class_='location')
            if location_elem:
                venue = location_elem.get_text(strip=True)
                if 'Branch' not in venue and venue != 'Dallas Public Library':
                    venue = f"{venue} Branch - Dallas Public Library"
            
            # Get address if available
            address = ''
            address_elem = soup.find('div', class_='street-address')
            if address_elem:
                address = address_elem.get_text(strip=True)
            
            # Get image - try multiple methods to find real event images
            image_url = None
            
            # Method 1: Look for event image field (common in library CMS)
            event_image_div = soup.find('div', class_='field-name-field-event-image')
            if event_image_div:
                img = event_image_div.find('img')
                if img and img.get('src'):
                    image_url = img.get('src')
                    print(f"      📸 Found image via field-name-field-event-image")
            
            # Method 2: Look for any field-type-image
            if not image_url:
                image_field = soup.find('div', class_='field-type-image')
                if image_field:
                    img = image_field.find('img')
                    if img and img.get('src'):
                        image_url = img.get('src')
                        print(f"      📸 Found image via field-type-image")
            
            # Method 3: Look for main content images (first real image, not logo)
            if not image_url:
                all_imgs = soup.find_all('img')
                for img in all_imgs:
                    src = img.get('src', '')
                    # Skip logos and tiny images
                    if src and 'logo' not in src.lower() and 'icon' not in src.lower():
                        width = img.get('width', '999')
                        if width and str(width).isdigit() and int(width) > 100:
                            image_url = src
                            print(f"      📸 Found image via content scan")
                            break
            
            # Method 4: Meta image (but skip broken logo)
            if not image_url:
                meta_image = soup.find('meta', property='og:image')
                if meta_image:
                    image_url = meta_image.get('content')
                    # Skip if it's the broken site logo
                    if image_url and 'lm_custom_site_theme/logo' in image_url:
                        image_url = None
                        print(f"      ⚠️  Skipped broken logo")
            
            # Fix relative URLs
            if image_url:
                if image_url.startswith('/'):
                    image_url = self.base_url + image_url
                print(f"      ✓ Image: {image_url[:60]}...")
            else:
                print(f"      ℹ️  No image found - will use category placeholder")
            
            # Categorize event
            category = self._categorize_event(title, description)
            
            # If no image found, use category-based placeholder
            if not image_url:
                category_images = {
                    'Reading & Literacy': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&q=80',  # Books
                    'Arts & Crafts': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800&q=80',  # Art supplies
                    'STEM & Technology': 'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&q=80',  # Technology
                    'Education & Learning': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80',  # Learning
                    'Music & Performance': 'https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=800&q=80',  # Music
                    'Teen & Youth': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80',  # Teens
                    'Digital Literacy': 'https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=800&q=80',  # Computer
                    'Community & Culture': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800&q=80'  # Library
                }
                image_url = category_images.get(category, category_images['Community & Culture'])
                print(f"      🎨 Using {category} placeholder")
            
            # Determine if family-friendly (most library events are!)
            is_family_friendly = self._is_family_friendly(title, description)
            
            return {
                'title': title,
                'description': description[:500] if description else None,
                'start_at': start_at.isoformat(),
                'end_at': None,  # Library events often don't list end times
                'venue': venue,
                'address': address or 'Various Dallas Public Library locations',
                'city': 'Dallas',
                'price_tier': 'FREE',  # Library events are FREE!
                'price_amount': None,
                'image_url': image_url,
                'source_url': url,
                'source_type': 'DALLAS_LIBRARY',
                'category': category,
                'is_family_friendly': is_family_friendly,
                'organizer': 'Dallas Public Library'
            }
        except Exception as e:
            print(f"      ⚠️  Parse error: {str(e)[:50]}")
            return None
    
    def _is_family_friendly(self, title: str, description: str) -> bool:
        """Determine if event is family-friendly"""
        text = f"{title} {description}".lower()
        
        # Family-friendly keywords
        family_keywords = [
            'kid', 'child', 'family', 'toddler', 'preschool', 'storytime',
            'story time', 'youth', 'teen', 'craft', 'stem', 'homework'
        ]
        
        # Adult-only keywords
        adult_keywords = ['adult only', '18+', '21+']
        
        for keyword in adult_keywords:
            if keyword in text:
                return False
        
        for keyword in family_keywords:
            if keyword in text:
                return True
        
        # Default to True for library events (most are family-friendly)
        return True
    
    def _categorize_event(self, title: str, description: str) -> str:
        """Categorize event based on content"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['storytime', 'story time', 'reading', 'book']):
            return 'Reading & Literacy'
        elif any(word in text for word in ['craft', 'art', 'paint', 'draw', 'creative']):
            return 'Arts & Crafts'
        elif any(word in text for word in ['stem', 'science', 'tech', 'coding', 'robot']):
            return 'STEM & Technology'
        elif any(word in text for word in ['homework', 'tutor', 'learning', 'class']):
            return 'Education & Learning'
        elif any(word in text for word in ['music', 'concert', 'performance']):
            return 'Music & Performance'
        elif any(word in text for word in ['teen', 'youth', 'young adult']):
            return 'Teen & Youth'
        elif any(word in text for word in ['computer', 'digital', 'internet']):
            return 'Digital Literacy'
        else:
            return 'Community & Culture'


def extract_dallas_library_events() -> List[Dict]:
    """Main function to extract Dallas Public Library events"""
    extractor = DallasLibraryExtractor()
    return extractor.fetch_events()


# For testing
if __name__ == "__main__":
    events = extract_dallas_library_events()
    print(f"\n📊 Extracted {len(events)} events")
    if events:
        print(f"\n📝 Sample Event:")
        print(json.dumps(events[0], indent=2, default=str))

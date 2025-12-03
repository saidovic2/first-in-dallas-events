"""
Investigate Dallas Arboretum website structure for better scraping
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.dallasarboretum.org'
EVENTS_URL = f'{BASE_URL}/events-activities/'

print("🔍 Analyzing Dallas Arboretum Events Page...\n")

try:
    response = requests.get(
        EVENTS_URL,
        timeout=30,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for pagination
    print("📄 Checking for pagination...")
    pagination = soup.find_all(['a', 'button'], class_=lambda x: x and ('page' in x.lower() or 'next' in x.lower() or 'load' in x.lower()))
    if pagination:
        print(f"   ✅ Found {len(pagination)} pagination elements:")
        for p in pagination[:5]:
            print(f"      - {p.get_text(strip=True)} | href: {p.get('href')}")
    else:
        print("   ❌ No pagination found")
    
    # Check for "Load More" or infinite scroll
    print("\n🔄 Checking for Load More / Infinite Scroll...")
    load_more = soup.find_all(['button', 'a', 'div'], text=lambda x: x and ('load more' in x.lower() or 'show more' in x.lower()))
    if load_more:
        print(f"   ✅ Found {len(load_more)} 'Load More' elements")
    else:
        print("   ❌ No 'Load More' found")
    
    # Check for calendar links
    print("\n📅 Checking for calendar/archive links...")
    calendar_links = soup.find_all('a', href=lambda x: x and ('/calendar' in x or '/events' in x or '/archive' in x))
    if calendar_links:
        print(f"   ✅ Found {len(calendar_links)} calendar-related links:")
        for link in calendar_links[:10]:
            href = link.get('href')
            if href.startswith('/'):
                href = BASE_URL + href
            print(f"      - {link.get_text(strip=True)[:40]} | {href}")
    else:
        print("   ❌ No calendar links found")
    
    # Check for event cards
    print("\n🎫 Checking event card structure...")
    event_cards = soup.find_all(['article', 'div'], class_=lambda x: x and 'event' in x.lower())
    print(f"   Found {len(event_cards)} elements with 'event' in class name")
    
    # Check for JSON-LD events
    print("\n📦 Checking JSON-LD events...")
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    print(f"   Found {len(json_ld_scripts)} JSON-LD scripts")
    
    # Look for API endpoints in the page
    print("\n🔌 Checking for API endpoints...")
    api_hints = soup.find_all(['script', 'div'], attrs={'data-api': True})
    if api_hints:
        print(f"   ✅ Found {len(api_hints)} elements with data-api attributes")
        for hint in api_hints[:3]:
            print(f"      - {hint.get('data-api')}")
    else:
        print("   ❌ No obvious API hints found")
    
    print("\n" + "="*60)
    print("\n💡 Recommendations:")
    print("   - If pagination exists → Implement multi-page scraping")
    print("   - If Load More exists → Implement progressive loading")
    print("   - If calendar exists → Scrape from calendar view")
    print("   - If no pagination → Current 8 events is the limit")
    
except Exception as e:
    print(f"❌ Error: {e}")

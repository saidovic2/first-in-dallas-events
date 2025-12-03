import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from extractors.dallas_library import DallasLibraryExtractor

# Test the scraper
extractor = DallasLibraryExtractor()

# Test fetching one specific event
test_url = 'https://dallaslibrary.librarymarket.com/event/awkward-family-photos-469011'

print(f"\n{'='*80}")
print(f"Testing Dallas Library Image Extraction")
print(f"URL: {test_url}")
print('='*80)

event_data = extractor._fetch_event_details(test_url)

if event_data:
    print(f"\n✅ Event Found:")
    print(f"   Title: {event_data['title']}")
    print(f"   Image URL: {event_data.get('image_url', 'NO IMAGE')}")
    print(f"   Category: {event_data.get('category', 'N/A')}")
else:
    print("\n❌ Failed to extract event")

"""
Test the enhanced Dallas Arboretum scraper
"""
import sys
sys.path.append('worker')

from extractors.dallas_arboretum import extract_dallas_arboretum_events

print("🧪 Testing Enhanced Dallas Arboretum Scraper\n")
print("=" * 60)

events = extract_dallas_arboretum_events()

print("\n" + "=" * 60)
print(f"\n📊 RESULTS:")
print(f"   Total events fetched: {len(events)}")

if events:
    print(f"\n📝 Sample Events:")
    for i, event in enumerate(events[:5], 1):
        print(f"\n   {i}. {event['title']}")
        print(f"      Date: {event['start_at']}")
        print(f"      Venue: {event['venue']}")
        print(f"      Category: {event.get('category', 'N/A')}")
        print(f"      Family Friendly: {event.get('is_family_friendly', False)}")
        print(f"      Image: {'✅ Yes' if event.get('image_url') else '❌ No'}")
else:
    print("   ❌ No events found")

print("\n" + "=" * 60)

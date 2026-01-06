"""Check new Apify dataset"""
import requests
import json

DATASET_ID = "wrMOybEHy5UW00HNh"
API_TOKEN = "apify_api_SyxGrvd54Tx0gfbRlbqfIK823e4Bf11UutCW"

print("\nFetching new dataset info...\n")

# Get dataset info
dataset_url = f"https://api.apify.com/v2/datasets/{DATASET_ID}?token={API_TOKEN}"
response = requests.get(dataset_url)
dataset_info = response.json()['data']

item_count = dataset_info.get('itemCount', 0)

print(f"Dataset ID: {DATASET_ID}")
print(f"Total events: {item_count}")
print(f"{'='*80}\n")

# Get first 3 events to check structure
items_url = f"https://api.apify.com/v2/datasets/{DATASET_ID}/items?token={API_TOKEN}&limit=3"
response = requests.get(items_url)
events = response.json()

print("Sample events from new actor:\n")

for i, event in enumerate(events[:3], 1):
    print(f"\n--- Event {i} ---")
    print(f"Name: {event.get('name', 'N/A')}")
    print(f"URL: {event.get('url', 'N/A')}")
    print(f"Image: {event.get('image', 'N/A')[:100]}...")
    print(f"Date: {event.get('dateTitle', 'N/A')}")
    print(f"Venue: {event.get('addressLocality', 'N/A')}")
    print(f"Segment: {event.get('segmentName', 'N/A')}")
    
    # Check image pattern
    image_url = event.get('image', '')
    if 'RECOMENDATION' in image_url:
        print(f"⚠️  Image pattern: RECOMENDATION (will be upgraded to HD)")
    elif 'RETINA_PORTRAIT' in image_url:
        print(f"⚠️  Image pattern: RETINA_PORTRAIT (will be upgraded to HD)")
    elif 'RETINA_LANDSCAPE_LARGE' in image_url:
        print(f"✓ Image pattern: Already HD!")
    else:
        print(f"Image pattern: Other (will check if upgrade needed)")

print(f"\n{'='*80}")
print(f"\n✓ Dataset has {item_count} events")
print(f"✓ Ready to import with high-res image conversion!")
print(f"✓ All images will be upgraded to 2048x1152 resolution")
print(f"✓ All URLs will have affiliate tracking (ID: 6497023)")
print()

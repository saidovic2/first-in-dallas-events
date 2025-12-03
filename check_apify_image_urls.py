"""Check what image URLs Apify is providing"""
import requests

APIFY_API_TOKEN = "apify_api_SyxGrvd54Tx0gfbRlbqfIK823e4Bf11UutCW"
DATASET_ID = "tTjM7nfqGag5B4nE9"

print("Fetching Apify dataset to check image URLs...\n")

dataset_url = f"https://api.apify.com/v2/datasets/{DATASET_ID}/items?token={APIFY_API_TOKEN}&limit=5"
response = requests.get(dataset_url)
events = response.json()

print(f"Sample image URLs from Apify:\n")
print("="*80)

for i, event in enumerate(events[:5], 1):
    print(f"\nEvent {i}: {event.get('name', 'N/A')[:50]}")
    print(f"Image URL: {event.get('image', 'N/A')}")
    print(f"Event URL: {event.get('url', 'N/A')}")
    
print("\n" + "="*80)

"""
Quick test to verify Ticketmaster API key works
"""
import requests

# Your API key
API_KEY = "5J6gVlhTbffU8kyFbTL5jeIqpkorcmQO"

# Test endpoint - search for events in Dallas
url = "https://app.ticketmaster.com/discovery/v2/events.json"
params = {
    "apikey": API_KEY,
    "city": "Dallas",
    "stateCode": "TX",
    "size": 5
}

print("🧪 Testing Ticketmaster API Key...")
print(f"Key: {API_KEY}")
print(f"URL: {url}")
print()

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        print("✅ SUCCESS! API key is valid!")
        data = response.json()
        
        if "_embedded" in data and "events" in data["_embedded"]:
            events = data["_embedded"]["events"]
            print(f"✅ Found {len(events)} events!")
            print()
            print("Sample events:")
            for event in events[:3]:
                print(f"  - {event.get('name')}")
        else:
            print("⚠️  No events found (but API key is valid)")
    
    elif response.status_code == 401:
        print("❌ UNAUTHORIZED - API Key is invalid or not activated")
        print()
        print("Possible fixes:")
        print("1. Check if you copied the Consumer Key (not Consumer Secret)")
        print("2. Verify your app is approved in Ticketmaster Developer Portal")
        print("3. Check if there are IP restrictions on your key")
        print("4. Try generating a new API key")
        print()
        print("Response:")
        print(response.text)
    
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Exception: {e}")

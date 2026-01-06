"""Test API endpoint directly"""
import requests

# Test local API
API_URL = "http://localhost:8001"  # Your FastAPI runs on 8001

# Get auth token first (you need to log in)
try:
    print(f"Testing API at: {API_URL}")
    print("\nStep 1: Logging in...")
    
    login_response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"email": "admin@firstindallas.com", "password": "admin"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        print(f"   ✓ Logged in successfully")
        
        print("\nStep 2: Fetching events...")
        
        # Get all events (no filters)
        events_response = requests.get(
            f"{API_URL}/api/events/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if events_response.status_code == 200:
            events = events_response.json()
            print(f"   ✓ Got {len(events)} events")
            
            # Count by status
            draft_count = len([e for e in events if e.get('status') == 'DRAFT'])
            published_count = len([e for e in events if e.get('status') == 'PUBLISHED'])
            
            print(f"\n   DRAFT: {draft_count}")
            print(f"   PUBLISHED: {published_count}")
            
            # Show first 5 Ticketmaster events
            ticketmaster_events = [e for e in events if e.get('source_type') == 'TICKETMASTER']
            print(f"\n   Ticketmaster events: {len(ticketmaster_events)}")
            
            if ticketmaster_events:
                print("\n   First 5 Ticketmaster events:")
                for event in ticketmaster_events[:5]:
                    print(f"   - [{event['id']}] {event['title'][:50]}")
                    print(f"     Date: {event['start_at']} | Status: {event['status']}")
            else:
                print("   ⚠️ NO Ticketmaster events in API response!")
                print(f"\n   Sample event sources:")
                sources = {}
                for e in events[:20]:
                    src = e.get('source_type', 'Unknown')
                    sources[src] = sources.get(src, 0) + 1
                for src, count in sources.items():
                    print(f"     - {src}: {count}")
        else:
            print(f"   ✗ Failed to get events: {events_response.status_code}")
            print(f"   {events_response.text}")
    else:
        print(f"   ✗ Login failed: {login_response.status_code}")
        print(f"   {login_response.text}")
        
except requests.exceptions.ConnectionError:
    print(f"\n✗ Cannot connect to API at {API_URL}")
    print("   Make sure your FastAPI server is running!")
    print("   Run: uvicorn main:app --reload --port 8001")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

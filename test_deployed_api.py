"""Test deployed Railway API"""
import requests

# Your deployed Railway API
API_URL = "https://first-in-dallas-events-production.up.railway.app"

try:
    print(f"Testing deployed API at: {API_URL}\n")
    
    # Try to get events without auth (should work for list)
    print("Step 1: Testing /api/events/ endpoint...")
    
    events_response = requests.get(
        f"{API_URL}/api/events/",
        params={"limit": 10},
        timeout=30
    )
    
    print(f"   Status code: {events_response.status_code}")
    
    if events_response.status_code == 200:
        events = events_response.json()
        print(f"   ✓ Got {len(events)} events")
        
        if events:
            # Count by status and source
            by_status = {}
            by_source = {}
            
            for e in events:
                status = e.get('status', 'Unknown')
                source = e.get('source_type', 'Unknown')
                by_status[status] = by_status.get(status, 0) + 1
                by_source[source] = by_source.get(source, 0) + 1
            
            print(f"\n   By Status:")
            for status, count in by_status.items():
                print(f"     {status}: {count}")
            
            print(f"\n   By Source:")
            for source, count in by_source.items():
                print(f"     {source}: {count}")
            
            print(f"\n   First 3 events:")
            for event in events[:3]:
                print(f"   - [{event['id']}] {event['title'][:50]}")
                print(f"     Status: {event['status']} | Source: {event.get('source_type')}")
        else:
            print("   ✗ API returned 0 events!")
            
    elif events_response.status_code == 401:
        print(f"   ✗ Unauthorized - need to login")
        
        # Try with login
        print("\nStep 2: Logging in...")
        login_response = requests.post(
            f"{API_URL}/api/auth/login",
            json={"email": "admin@firstindallas.com", "password": "admin"},
            timeout=30
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            print(f"   ✓ Logged in")
            
            # Retry with token
            print("\nStep 3: Fetching events with auth...")
            events_response = requests.get(
                f"{API_URL}/api/events/",
                headers={"Authorization": f"Bearer {token}"},
                params={"limit": 200},
                timeout=30
            )
            
            if events_response.status_code == 200:
                events = events_response.json()
                print(f"   ✓ Got {len(events)} events")
                
                # Count Ticketmaster
                ticketmaster = [e for e in events if e.get('source_type') == 'TICKETMASTER']
                print(f"   Ticketmaster events: {len(ticketmaster)}")
                
                if ticketmaster:
                    print(f"\n   First 5 Ticketmaster events:")
                    for event in ticketmaster[:5]:
                        print(f"   - [{event['id']}] {event['title'][:50]}")
            else:
                print(f"   ✗ Failed: {events_response.status_code}")
                print(f"   {events_response.text[:200]}")
        else:
            print(f"   ✗ Login failed: {login_response.status_code}")
    else:
        print(f"   ✗ Failed: {events_response.status_code}")
        print(f"   Response: {events_response.text[:500]}")
        
except requests.exceptions.Timeout:
    print(f"\n✗ Request timed out - Railway may be sleeping")
    print("   Try visiting the URL in browser first to wake it up")
    
except requests.exceptions.ConnectionError:
    print(f"\n✗ Cannot connect to {API_URL}")
    print("   Check if Railway deployment is running")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

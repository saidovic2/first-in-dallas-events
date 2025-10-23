import os
import requests
import time
from dateutil import parser as date_parser
import re

def bulk_sync_facebook_dallas():
    """
    Bulk sync Facebook events from Dallas, Plano, Arlington, and Fort Worth
    Uses Apify to search by location
    """
    api_token = os.getenv('APIFY_API_TOKEN')
    
    if not api_token:
        print("⚠️  APIFY_API_TOKEN not set. Cannot sync Facebook events.")
        return []
    
    # Define locations to search
    locations = [
        "Dallas, TX",
        "Plano, TX",
        "Arlington, TX",
        "Fort Worth, TX"
    ]
    
    all_events = []
    
    for location in locations:
        print(f"\n🔍 Syncing Facebook events from: {location}")
        events = search_facebook_by_location(location, api_token)
        if events:
            all_events.extend(events)
            print(f"✅ Found {len(events)} events in {location}")
        else:
            print(f"⚠️  No events found in {location}")
        
        # Small delay between locations to avoid rate limits
        time.sleep(2)
    
    print(f"\n🎉 Total Facebook events found: {len(all_events)}")
    return all_events

def search_facebook_by_location(location, api_token, max_results=50):
    """
    Search Facebook events by location using Apify
    """
    try:
        actor_id = "apify~facebook-events-scraper"
        
        print(f"🔍 Searching Facebook for: {location}")
        
        # Use searchQueries parameter (like in Apify Console)
        run_input = {
            "searchQueries": [location],  # Use searchQueries for location-based search
            "startUrls": [],  # Empty startUrls when using searchQueries
            "maxEvents": max_results,
            "proxyConfiguration": {
                "useApifyProxy": True
            }
        }
        
        # Start the Apify actor
        run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        print(f"📤 Starting Apify search for: {location}")
        response = requests.post(run_url, json=run_input, headers=headers, timeout=30)
        response.raise_for_status()
        
        run_data = response.json()
        run_id = run_data["data"]["id"]
        
        print(f"⏳ Waiting for Apify to complete (Run ID: {run_id})...")
        
        # Wait for the run to complete (max 3 minutes for bulk search)
        max_wait = 180  # seconds
        wait_interval = 10  # seconds
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval
            
            # Check run status
            status_url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}"
            status_response = requests.get(status_url, headers=headers, timeout=10)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            status = status_data["data"]["status"]
            
            if elapsed % 30 == 0:  # Print every 30 seconds
                print(f"⏳ Status: {status} ({elapsed}s elapsed)")
            
            if status == "SUCCEEDED":
                print(f"✅ Apify search completed for {location}!")
                break
            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                print(f"❌ Apify run failed with status: {status}")
                return []
        else:
            print(f"⏱️  Timeout waiting for Apify run")
            return []
        
        # Fetch results
        print(f"📥 Fetching results for {location}...")
        dataset_id = status_data["data"]["defaultDatasetId"]
        results_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        
        results_response = requests.get(results_url, headers=headers, timeout=30)
        results_response.raise_for_status()
        
        items = results_response.json()
        
        # Parse events
        from extractors.apify_facebook import parse_apify_event
        
        events = []
        for item in items:
            event = parse_apify_event(item, f"https://facebook.com/events/{item.get('id', '')}")
            if event:
                events.append(event)
        
        return events
    
    except Exception as e:
        print(f"❌ Error searching Facebook for {location}: {e}")
        import traceback
        traceback.print_exc()
        return []

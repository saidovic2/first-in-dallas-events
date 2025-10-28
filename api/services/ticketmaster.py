"""
Ticketmaster API Integration Service
Fetches events from Ticketmaster Discovery API
"""

import requests
from typing import Optional, List, Dict
from datetime import datetime
import os

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY", "")
TICKETMASTER_BASE_URL = "https://app.ticketmaster.com/discovery/v2"


class TicketmasterService:
    """Service to interact with Ticketmaster Discovery API"""
    
    def __init__(self, api_key: str = TICKETMASTER_API_KEY):
        self.api_key = api_key
        self.base_url = TICKETMASTER_BASE_URL
    
    def search_events(
        self,
        city: str = "Dallas",
        state_code: str = "TX",
        country_code: str = "US",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        keyword: Optional[str] = None,
        classification: Optional[str] = None,
        size: int = 20,
        page: int = 0
    ) -> Dict:
        """
        Search for events on Ticketmaster
        
        Args:
            city: City name (e.g., "Dallas")
            state_code: State code (e.g., "TX")
            country_code: Country code (e.g., "US")
            start_date: Start date in ISO format (e.g., "2024-01-01T00:00:00Z")
            end_date: End date in ISO format
            keyword: Search keyword
            classification: Event category (e.g., "music", "sports")
            size: Number of results per page (max 200)
            page: Page number
        
        Returns:
            Dict containing events and metadata
        """
        endpoint = f"{self.base_url}/events.json"
        
        params = {
            "apikey": self.api_key,
            "city": city,
            "stateCode": state_code,
            "countryCode": country_code,
            "size": size,
            "page": page,
            "sort": "date,asc"  # Sort by date, earliest first
        }
        
        # Optional parameters
        if start_date:
            params["startDateTime"] = start_date
        if end_date:
            params["endDateTime"] = end_date
        if keyword:
            params["keyword"] = keyword
        if classification:
            params["classificationName"] = classification
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ticketmaster API Error: {e}")
            return {"error": str(e)}
    
    def get_event_details(self, event_id: str) -> Dict:
        """
        Get detailed information about a specific event
        
        Args:
            event_id: Ticketmaster event ID
        
        Returns:
            Dict containing event details
        """
        endpoint = f"{self.base_url}/events/{event_id}.json"
        params = {"apikey": self.api_key}
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Ticketmaster API Error: {e}")
            return {"error": str(e)}
    
    def transform_to_local_event(self, tm_event: Dict) -> Dict:
        """
        Transform Ticketmaster event data to match your local event structure
        
        Args:
            tm_event: Raw Ticketmaster event data
        
        Returns:
            Dict formatted for your database
        """
        # Extract venue information
        venue_info = tm_event.get("_embedded", {}).get("venues", [{}])[0]
        venue_name = venue_info.get("name", "")
        venue_address = venue_info.get("address", {}).get("line1", "")
        venue_city = venue_info.get("city", {}).get("name", "")
        venue_state = venue_info.get("state", {}).get("stateCode", "")
        venue_zip = venue_info.get("postalCode", "")
        venue_location = venue_info.get("location", {})
        
        # Extract date/time
        dates = tm_event.get("dates", {})
        start_date = dates.get("start", {})
        start_datetime = start_date.get("dateTime", "")
        
        # Extract images
        images = tm_event.get("images", [])
        image_url = images[0].get("url", "") if images else ""
        
        # Extract pricing
        price_ranges = tm_event.get("priceRanges", [])
        min_price = price_ranges[0].get("min", None) if price_ranges else None
        max_price = price_ranges[0].get("max", None) if price_ranges else None
        
        # Determine price tier
        if not price_ranges:
            price_tier = "FREE"
        elif min_price and min_price > 50:
            price_tier = "PREMIUM"
        else:
            price_tier = "PAID"
        
        # Extract classification (category)
        classifications = tm_event.get("classifications", [{}])
        segment = classifications[0].get("segment", {}).get("name", "GENERAL")
        
        # Build transformed event
        return {
            "title": tm_event.get("name", ""),
            "description": tm_event.get("info", tm_event.get("pleaseNote", "")),
            "primary_url": tm_event.get("url", ""),
            "venue": venue_name,
            "address": venue_address,
            "city": venue_city,
            "state": venue_state,
            "zip_code": venue_zip,
            "country": "USA",
            "latitude": venue_location.get("latitude"),
            "longitude": venue_location.get("longitude"),
            "start_at": start_datetime,
            "image_url": image_url,
            "price_amount": min_price,
            "price_tier": price_tier,
            "category": "FEATURED" if price_tier == "PREMIUM" else "STANDARD",
            "status": "PUBLISHED",
            "source_type": "TICKETMASTER",
            "external_id": tm_event.get("id"),
            "format": "IN_PERSON"
        }


# Example usage
if __name__ == "__main__":
    # Test the service
    service = TicketmasterService()
    
    # Search for events in Dallas
    results = service.search_events(city="Dallas", state_code="TX", size=5)
    
    if "error" not in results:
        events = results.get("_embedded", {}).get("events", [])
        print(f"Found {len(events)} events in Dallas")
        
        for event in events:
            print(f"- {event.get('name')}")
            local_event = service.transform_to_local_event(event)
            print(f"  Transformed: {local_event.get('title')}")
    else:
        print(f"Error: {results['error']}")

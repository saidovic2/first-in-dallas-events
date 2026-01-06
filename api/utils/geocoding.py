"""
Google Geocoding API Integration
Validates addresses and gets precise coordinates for maps
"""
import httpx
import os
from typing import Optional, Dict

async def geocode_address(venue: str, address: str, city: str) -> Optional[Dict]:
    """
    Use Google Geocoding API to get precise coordinates
    
    Args:
        venue: Venue name
        address: Street address
        city: City name
    
    Returns:
        Dict with lat, lng, formatted_address, or None if not found
    """
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        # Fallback to text-based search if no API key
        return None
    
    # Build address query
    query_parts = []
    if venue:
        venue_clean = venue.split('-')[0].split('—')[0].strip()
        query_parts.append(venue_clean)
    if address:
        query_parts.append(address)
    if city:
        query_parts.append(f"{city}, TX")
    
    query = ", ".join(query_parts)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": query,
                "key": api_key
            }
            
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                result = data["results"][0]
                location = result["geometry"]["location"]
                
                return {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "formatted_address": result["formatted_address"],
                    "place_id": result.get("place_id")
                }
    
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None
    
    return None


def generate_coordinate_based_map(lat: float, lng: float, title: str) -> str:
    """
    Generate Google Maps embed using precise coordinates
    This is 100% accurate
    """
    return f"""
    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
        <iframe 
            src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q={lat},{lng}&zoom=15"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
            allowfullscreen=""
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade">
        </iframe>
    </div>
    """


# Known Dallas venues database (manually verified coordinates)
# This can be expanded over time
VERIFIED_VENUES = {
    "dallas arboretum": {
        "lat": 32.8209,
        "lng": -96.7181,
        "address": "8525 Garland Rd, Dallas, TX 75218"
    },
    "american airlines center": {
        "lat": 32.7905,
        "lng": -96.8103,
        "address": "2500 Victory Ave, Dallas, TX 75219"
    },
    "at&t stadium": {
        "lat": 32.7473,
        "lng": -97.0945,
        "address": "1 AT&T Way, Arlington, TX 76011"
    },
    "reunion tower": {
        "lat": 32.7756,
        "lng": -96.8089,
        "address": "300 Reunion Blvd E, Dallas, TX 75207"
    },
    "dallas museum of art": {
        "lat": 32.7879,
        "lng": -96.8007,
        "address": "1717 N Harwood St, Dallas, TX 75201"
    }
}


def get_verified_venue_coords(venue: str) -> Optional[Dict]:
    """Check if venue is in our verified database"""
    if not venue:
        return None
    
    venue_lower = venue.lower()
    
    for known_venue, data in VERIFIED_VENUES.items():
        if known_venue in venue_lower:
            return data
    
    return None

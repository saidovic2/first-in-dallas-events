import httpx
from config import settings
from models.event import Event

async def publish_to_wordpress(event: Event) -> int:
    """Publish an event to WordPress"""
    if not all([settings.WP_BASE_URL, settings.WP_USER, settings.WP_APP_PASSWORD]):
        raise Exception("WordPress credentials not configured")
    
    # Prepare post data
    post_data = {
        "title": event.title,
        "content": f"""
        <div class="event-details">
            <p><strong>Date:</strong> {event.start_at.strftime('%B %d, %Y at %I:%M %p')}</p>
            {f'<p><strong>End:</strong> {event.end_at.strftime("%B %d, %Y at %I:%M %p")}</p>' if event.end_at else ''}
            {f'<p><strong>Venue:</strong> {event.venue}</p>' if event.venue else ''}
            {f'<p><strong>Address:</strong> {event.address}</p>' if event.address else ''}
            {f'<p><strong>City:</strong> {event.city}</p>' if event.city else ''}
            {f'<p><strong>Price:</strong> {event.price_tier.upper()}</p>' if event.price_tier else ''}
            <p><strong>Source:</strong> <a href="{event.source_url}" target="_blank">View Original</a></p>
        </div>
        <div class="event-description">
            {event.description or ''}
        </div>
        """,
        "status": "publish",
        "categories": [1],  # Default category
        "meta": {
            "event_start": event.start_at.isoformat(),
            "event_venue": event.venue or "",
            "event_city": event.city or "",
        }
    }
    
    # Make request to WordPress REST API
    auth = (settings.WP_USER, settings.WP_APP_PASSWORD)
    url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/posts"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=post_data, auth=auth)
        response.raise_for_status()
        result = response.json()
        return result["id"]

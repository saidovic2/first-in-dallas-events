import httpx
import os
import urllib.parse
import re
from config import settings
from models.event import Event

# Cache for Events category ID
_events_category_id = None

async def upload_image_to_wordpress(image_url: str, title: str, alt_text: str) -> int:
    """
    Download image from URL and upload to WordPress Media Library
    Returns media ID for use as featured image
    """
    if not image_url:
        return None
    
    try:
        # Download image
        async with httpx.AsyncClient(timeout=30.0) as client:
            img_response = await client.get(image_url)
            img_response.raise_for_status()
            
            # Get filename from URL or generate one
            filename = os.path.basename(urllib.parse.urlparse(image_url).path)
            if not filename or '.' not in filename:
                filename = f"event-{title[:30].replace(' ', '-').lower()}.jpg"
            
            # Get content type
            content_type = img_response.headers.get('content-type', 'image/jpeg')
            
            # Prepare multipart upload
            files = {
                'file': (filename, img_response.content, content_type)
            }
            
            # Upload to WordPress
            auth = (settings.WP_USER, settings.WP_APP_PASSWORD)
            upload_url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/media"
            
            upload_response = await client.post(
                upload_url,
                files=files,
                auth=auth,
                data={
                    'title': title,
                    'alt_text': alt_text,
                    'caption': '',
                }
            )
            
            upload_response.raise_for_status()
            result = upload_response.json()
            return result['id']
            
    except Exception as e:
        print(f"Failed to upload image: {e}")
        return None

def extract_meta_description(html_content: str, max_length: int = 155) -> str:
    """Extract plain text from HTML and create SEO meta description"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html_content)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    return text

async def get_events_category_id() -> int:
    """Get or create the 'Events' category in WordPress"""
    global _events_category_id
    
    if _events_category_id:
        return _events_category_id
    
    auth = (settings.WP_USER, settings.WP_APP_PASSWORD)
    
    # Search for existing 'Events' category
    async with httpx.AsyncClient() as client:
        search_url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/categories?search=Events"
        response = await client.get(search_url, auth=auth)
        
        if response.status_code == 200:
            categories = response.json()
            for cat in categories:
                if cat['name'].lower() == 'events':
                    _events_category_id = cat['id']
                    return _events_category_id
        
        # Create 'Events' category if it doesn't exist
        create_url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/categories"
        cat_data = {"name": "Events", "slug": "events"}
        response = await client.post(create_url, json=cat_data, auth=auth)
        
        if response.status_code == 201:
            result = response.json()
            _events_category_id = result['id']
            return _events_category_id
        
        # Fallback to default category
        return 1

async def get_or_create_past_events_category() -> int:
    """Get or create the 'Past Events' category in WordPress for SEO-friendly archiving"""
    auth = (settings.WP_USER, settings.WP_APP_PASSWORD)
    
    async with httpx.AsyncClient() as client:
        # Search for existing 'Past Events' category
        search_url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/categories?search=Past Events"
        response = await client.get(search_url, auth=auth)
        
        if response.status_code == 200:
            categories = response.json()
            for cat in categories:
                if cat['name'].lower() == 'past events':
                    return cat['id']
        
        # Create 'Past Events' category if it doesn't exist
        create_url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/categories"
        cat_data = {
            "name": "Past Events",
            "slug": "past-events",
            "description": "Archive of past events for SEO preservation"
        }
        response = await client.post(create_url, json=cat_data, auth=auth)
        
        if response.status_code == 201:
            result = response.json()
            return result['id']
        
        # Fallback to default category
        return 1

async def archive_past_wordpress_events(hours_after: int = 24) -> dict:
    """
    Archive WordPress posts for events that ended 24+ hours ago
    Moves posts to 'Past Events' category instead of deleting for SEO preservation
    
    Args:
        hours_after: Hours after event date to archive (default 24)
    
    Returns:
        dict with archiving stats
    """
    from datetime import datetime, timedelta, timezone
    
    if not all([settings.WP_BASE_URL, settings.WP_USER, settings.WP_APP_PASSWORD]):
        raise Exception("WordPress credentials not configured")
    
    auth = (settings.WP_USER, settings.WP_APP_PASSWORD)
    events_category_id = await get_events_category_id()
    
    # Get or create 'Past Events' category
    past_events_category_id = await get_or_create_past_events_category()
    
    # Calculate cutoff time (24 hours ago)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_after)
    
    archived_count = 0
    posts_checked = 0
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Get all published posts in Events category
        page = 1
        per_page = 100
        
        while True:
            url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/posts"
            params = {
                "categories": events_category_id,
                "status": "publish",
                "per_page": per_page,
                "page": page,
                "_fields": "id,title,meta.event_start"
            }
            
            response = await client.get(url, params=params, auth=auth)
            
            if response.status_code != 200:
                break
            
            posts = response.json()
            
            if not posts:
                break
            
            for post in posts:
                posts_checked += 1
                
                # Get event start time from meta
                event_start_str = post.get("meta", {}).get("event_start")
                
                if not event_start_str:
                    continue
                
                # Parse event date
                try:
                    event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
                    
                    # Check if event is past cutoff time
                    if event_start < cutoff_time:
                        # Archive: Move to 'Past Events' category
                        archive_url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/posts/{post['id']}"
                        archive_data = {
                            "categories": [past_events_category_id],
                            "title": f"[PAST EVENT] {post.get('title', {}).get('rendered', 'Unknown') if isinstance(post.get('title'), dict) else post.get('title', 'Unknown')}"
                        }
                        archive_response = await client.post(archive_url, json=archive_data, auth=auth)
                        
                        if archive_response.status_code == 200:
                            archived_count += 1
                            title = post.get('title', 'Unknown')
                            if isinstance(title, dict):
                                title = title.get('rendered', 'Unknown')
                            print(f"  📦 Archived: {title}")
                
                except Exception as e:
                    print(f"  ⚠️  Error processing post {post['id']}: {e}")
                    continue
            
            # Check if there are more pages
            if len(posts) < per_page:
                break
            
            page += 1
    
    return {
        "posts_checked": posts_checked,
        "archived_count": archived_count,
        "cutoff_time": cutoff_time.isoformat()
    }

def generate_breadcrumb_schema(event: Event) -> str:
    """Generate Schema.org BreadcrumbList JSON-LD for rich snippets with geo-targeted keywords"""
    import json
    
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": f"{settings.WP_BASE_URL}"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Things to Do in Dallas",
                "item": f"{settings.WP_BASE_URL}/things-to-do-in-dallas"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": "Events",
                "item": f"{settings.WP_BASE_URL}/category/events"
            },
            {
                "@type": "ListItem",
                "position": 4,
                "name": event.title
            }
        ]
    }
    
    return f'<script type="application/ld+json">{json.dumps(breadcrumb_schema, ensure_ascii=False)}</script>'

def generate_event_schema(event: Event) -> str:
    """Generate Schema.org Event JSON-LD structured data"""
    import json
    from datetime import datetime
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": event.title,
        "description": event.description[:500] if event.description else "",
        "startDate": event.start_at.isoformat(),
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode"
    }
    
    # Add end date if available
    if event.end_at:
        schema["endDate"] = event.end_at.isoformat()
    
    # Add location
    if event.venue or event.address:
        location = {
            "@type": "Place",
            "name": event.venue or "Event Venue"
        }
        
        if event.address or event.city:
            location["address"] = {
                "@type": "PostalAddress",
                "streetAddress": event.address or "",
                "addressLocality": event.city or "Dallas",
                "addressRegion": "TX",
                "addressCountry": "US"
            }
        
        schema["location"] = location
    
    # Add image
    if event.image_url:
        schema["image"] = [event.image_url]
    
    # Add price/offers
    if event.price_tier:
        offer = {
            "@type": "Offer",
            "url": event.source_url or "",
            "availability": "https://schema.org/InStock"
        }
        
        if event.price_tier.lower() == "free":
            offer["price"] = "0"
            offer["priceCurrency"] = "USD"
        elif event.price_amount:
            offer["price"] = str(event.price_amount)
            offer["priceCurrency"] = "USD"
        
        schema["offers"] = offer
    
    # Add organizer
    schema["organizer"] = {
        "@type": "Organization",
        "name": "First in Dallas",
        "url": "https://firstindallas.com"
    }
    
    # Return as script tag
    json_str = json.dumps(schema, indent=2)
    return f'<script type="application/ld+json">\n{json_str}\n</script>'

def generate_google_maps_embed(venue: str, address: str, city: str) -> str:
    """Generate Google Maps embed HTML - only if we have good location data"""
    
    # Quality check: Only generate map if we have address or specific venue
    # This prevents inaccurate maps from vague venue names
    if not address and not venue:
        return ""
    
    # If we only have venue name without address, be more cautious
    if not address and venue:
        # Skip if venue name is too generic
        generic_names = ['downtown', 'city hall', 'park', 'arena', 'center', 'tba', 'tbd']
        if any(generic in venue.lower() for generic in generic_names):
            return ""
    
    # Build search query for Google Maps
    # Priority: Full address > Venue with city > Venue only
    location_parts = []
    
    # Clean up venue name (remove extra metadata)
    if venue:
        # Remove common separators and extra info after them
        venue_clean = venue.split('-')[0].split('—')[0].strip()
        location_parts.append(venue_clean)
    
    if address:
        location_parts.append(address)
    
    if city:
        location_parts.append(city)
        location_parts.append("TX")  # Add state for better accuracy
    
    location_query = ", ".join(location_parts)
    encoded_query = urllib.parse.quote(location_query)
    
    # Return responsive iframe embed
    return f"""
    <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 20px 0;">
        <iframe 
            src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q={encoded_query}"
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
            allowfullscreen=""
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade">
        </iframe>
    </div>
    """

async def publish_to_wordpress(event: Event, enhanced_description: str = None, post_id: int = None, auto_enhance: bool = True) -> int:
    """
    Publish or update an event on WordPress with full SEO optimization
    
    Args:
        event: Event object from database
        enhanced_description: Optional LLM-generated description (if None and auto_enhance=True, generates automatically)
        post_id: Optional WordPress post ID to update (if None, creates new post)
        auto_enhance: If True and enhanced_description is None, auto-generate E-E-A-T content via LLM
    
    Returns:
        WordPress post ID
    """
    if not all([settings.WP_BASE_URL, settings.WP_USER, settings.WP_APP_PASSWORD]):
        raise Exception("WordPress credentials not configured")
    
    # Auto-generate E-E-A-T content if not provided and auto_enhance is enabled
    if enhanced_description is None and auto_enhance:
        try:
            from utils.llm_enhancer import enhance_event_description
            print(f"   🤖 Generating E-E-A-T content for: {event.title[:50]}...")
            
            event_data = {
                "title": event.title,
                "description": event.description or "",
                "venue": event.venue or "",
                "city": event.city or "Dallas",
                "date": event.start_at.strftime('%B %d, %Y'),
                "price_tier": event.price_tier or "unknown"
            }
            
            enhanced_description = await enhance_event_description(event_data)
            print(f"   ✅ E-E-A-T content generated ({len(enhanced_description)} chars)")
        except Exception as e:
            print(f"   ⚠️  LLM enhancement failed: {e}. Using original description.")
            enhanced_description = None
    
    # Try to load custom template
    template_path = "api/templates/wordpress_event.html"
    content = ""
    
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
            
        # Format dates
        start_str = event.start_at.strftime('%B %d, %Y at %I:%M %p')
        end_str = event.end_at.strftime('%B %d, %Y at %I:%M %p') if event.end_at else ""
        price_str = f"{event.price_tier.upper()}"
        if event.price_amount:
            price_str += f" (${event.price_amount})"
        
        # Generate Google Maps embed
        maps_embed = generate_google_maps_embed(
            event.venue or "",
            event.address or "",
            event.city or ""
        )
        
        # Generate Schema.org Event JSON-LD
        event_schema = generate_event_schema(event)
        
        # Generate Breadcrumb Schema for rich snippets
        breadcrumb_schema = generate_breadcrumb_schema(event)
        
        # Use enhanced description if available, otherwise use original
        description = enhanced_description if enhanced_description else (event.description or "")
        
        # Optimize image alt text
        image_alt = f"{event.title} at {event.venue}" if event.venue else event.title
            
        # Replace placeholders
        content = template.replace("{{title}}", event.title or "") \
                         .replace("{{description}}", description) \
                         .replace("{{start_at}}", start_str) \
                         .replace("{{end_at}}", end_str) \
                         .replace("{{venue}}", event.venue or "") \
                         .replace("{{address}}", event.address or "") \
                         .replace("{{city}}", event.city or "") \
                         .replace("{{price}}", price_str) \
                         .replace("{{image_url}}", event.image_url or "") \
                         .replace("{{image_alt}}", image_alt) \
                         .replace("{{source_url}}", event.source_url or "") \
                         .replace("{{google_maps}}", maps_embed)
        
        # Add Schema.org JSON-LD at the BOTTOM of content (not top) so it's not visible
        # Include both Event schema and Breadcrumb schema for rich snippets
        content = content + "\n\n<!-- wp:html -->\n" + event_schema + "\n" + breadcrumb_schema + "\n<!-- /wp:html -->"
    else:
        # Fallback to default HTML
        content = f"""
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
        """

    # Get Events category ID
    events_category_id = await get_events_category_id()
    
    # Generate meta description from content
    meta_desc = extract_meta_description(
        enhanced_description if enhanced_description else (event.description or ""),
        max_length=155
    )
    
    # Upload featured image if available
    featured_media_id = None
    if event.image_url:
        print(f"   📷 Uploading featured image...")
        featured_media_id = await upload_image_to_wordpress(
            event.image_url,
            event.title,
            image_alt  # Use the same optimized alt text
        )
        if featured_media_id:
            print(f"   ✅ Featured image uploaded (Media ID: {featured_media_id})")
    
    # Prepare post data
    post_data = {
        "title": event.title,
        "content": content,
        "excerpt": "",  # Empty excerpt to prevent duplicate text under title
        "status": "publish",
        "categories": [events_category_id],
        "featured_media": featured_media_id if featured_media_id else 0,
        "meta": {
            "event_start": event.start_at.isoformat(),
            "event_venue": event.venue or "",
            "event_city": event.city or "",
            # Yoast SEO fields (if Yoast is installed)
            "_yoast_wpseo_metadesc": meta_desc,
            "_yoast_wpseo_opengraph-description": meta_desc,
            "_yoast_wpseo_twitter-description": meta_desc,
            "_yoast_wpseo_opengraph-image": event.image_url or "",
            "_yoast_wpseo_twitter-image": event.image_url or "",
            "_yoast_wpseo_canonical": "",  # Let Yoast auto-generate canonical URL
        }
    }
    
    # Make request to WordPress REST API
    auth = (settings.WP_USER, settings.WP_APP_PASSWORD)
    
    async with httpx.AsyncClient() as client:
        if post_id:
            # Update existing post
            url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/posts/{post_id}"
            response = await client.post(url, json=post_data, auth=auth)
        else:
            # Create new post
            url = f"{settings.WP_BASE_URL}/wp-json/wp/v2/posts"
            response = await client.post(url, json=post_data, auth=auth)
        
        response.raise_for_status()
        result = response.json()
        return result["id"]

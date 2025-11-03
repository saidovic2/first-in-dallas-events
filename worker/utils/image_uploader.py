"""
Image Uploader Utility
Downloads external images and uploads them to Supabase Storage
"""

import requests
import os
from supabase import create_client, Client
from typing import Optional
import hashlib
from urllib.parse import urlparse
import mimetypes

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("⚠️  Supabase credentials not found - image upload will be skipped")


def upload_external_image_to_supabase(image_url: str) -> Optional[str]:
    """
    Download an external image and upload it to Supabase Storage
    
    Args:
        image_url: External image URL (Facebook, Ticketmaster, etc.)
        
    Returns:
        Supabase public URL or None if upload fails
    """
    if not image_url or not supabase:
        return None
        
    try:
        # Generate unique filename based on URL hash
        url_hash = hashlib.md5(image_url.encode()).hexdigest()[:12]
        
        # Get file extension from URL or content-type
        parsed_url = urlparse(image_url)
        ext = os.path.splitext(parsed_url.path)[1]
        
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'  # Default to jpg
            
        filename = f"event-images/{url_hash}{ext}"
        
        # Check if already uploaded
        try:
            existing = supabase.storage.from_('events').get_public_url(filename)
            if existing:
                # Verify it exists
                check_response = requests.head(existing, timeout=5)
                if check_response.status_code == 200:
                    print(f"✅ Image already cached: {filename}")
                    return existing
        except:
            pass
        
        # Download the external image
        print(f"⬇️  Downloading image from: {image_url[:80]}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()
        
        # Get content type
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # Read image data
        image_data = response.content
        
        # Upload to Supabase Storage
        print(f"⬆️  Uploading to Supabase: {filename}")
        result = supabase.storage.from_('events').upload(
            filename,
            image_data,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_('events').get_public_url(filename)
        
        print(f"✅ Image uploaded successfully: {public_url[:80]}...")
        return public_url
        
    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout downloading image: {image_url[:80]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download image: {str(e)[:100]}")
        return None
    except Exception as e:
        print(f"❌ Failed to upload image to Supabase: {str(e)[:100]}")
        return None


def process_event_image(event_data: dict) -> dict:
    """
    Process an event's image_url by uploading it to Supabase if it's external
    
    Args:
        event_data: Event dictionary with image_url field
        
    Returns:
        Updated event dictionary with Supabase image URL
    """
    if not event_data.get('image_url'):
        return event_data
        
    external_url = event_data['image_url']
    
    # Skip if already a Supabase URL
    if SUPABASE_URL and SUPABASE_URL in external_url:
        print(f"✅ Image already in Supabase storage")
        return event_data
        
    # Upload to Supabase
    supabase_url = upload_external_image_to_supabase(external_url)
    
    if supabase_url:
        event_data['image_url'] = supabase_url
        print(f"🖼️  Image URL updated to Supabase storage")
    else:
        print(f"⚠️  Keeping original image URL (upload failed)")
        
    return event_data

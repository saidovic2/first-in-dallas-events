"""
Automatically fix Facebook event images by caching them to Supabase
This prevents broken images when Facebook blocks the URLs
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from supabase import create_client, Client

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not all([DATABASE_URL, SUPABASE_URL, SUPABASE_KEY]):
    print("❌ Missing environment variables!")
    exit(1)

engine = create_engine(DATABASE_URL)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*80)
print("🛡️  FIXING FACEBOOK EVENT IMAGES")
print("="*80)
print("\nThis will:")
print("1. Download Facebook event images from fbcdn.net")
print("2. Upload them to Supabase storage")
print("3. Update event records with permanent Supabase URLs")
print("4. Protect against broken Facebook image links\n")

def upload_image_to_supabase(image_url, event_id):
    """Download and upload image to Supabase"""
    try:
        response = requests.get(image_url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        response.raise_for_status()
        
        file_extension = 'jpg'
        if 'content-type' in response.headers:
            content_type = response.headers['content-type'].lower()
            if 'png' in content_type:
                file_extension = 'png'
            elif 'webp' in content_type:
                file_extension = 'webp'
        
        filename = f"facebook_events/{event_id}_{int(datetime.now().timestamp())}.{file_extension}"
        
        result = supabase.storage.from_('event-images').upload(
            filename,
            response.content,
            file_options={"content-type": f"image/{file_extension}"}
        )
        
        public_url = supabase.storage.from_('event-images').get_public_url(filename)
        
        return public_url
        
    except Exception as e:
        print(f"\n      Error details: {str(e)[:100]}")
        return None


def fix_facebook_images():
    """Cache Facebook event images to Supabase"""
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT id, title, image_url
            FROM events 
            WHERE source_type = 'FACEBOOK'
            AND image_url IS NOT NULL
            AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
            AND image_url NOT LIKE '%supabase%'
            ORDER BY id
        """))
        
        events = list(result)
        total = len(events)
        
        if total == 0:
            print("✅ All Facebook events already protected!\n")
            return
        
        print(f"📸 Found {total} Facebook events with broken image URLs")
        print(f"   Fixing them by caching to Supabase storage...\n")
        
        success = 0
        failed = 0
        
        for i, event in enumerate(events, 1):
            try:
                title_display = event.title[:50] + "..." if len(event.title) > 50 else event.title
                print(f"[{i}/{total}] {title_display}", end="", flush=True)
                
                supabase_url = upload_image_to_supabase(event.image_url, event.id)
                
                if supabase_url:
                    conn.execute(text("""
                        UPDATE events 
                        SET image_url = :new_url
                        WHERE id = :event_id
                    """), {"new_url": supabase_url, "event_id": event.id})
                    conn.commit()
                    
                    print(f" ✅")
                    success += 1
                else:
                    print(f" ❌")
                    failed += 1
                    
            except Exception as e:
                error_msg = str(e)[:60]
                print(f" ❌ {error_msg}")
                failed += 1
                conn.rollback()
        
        print(f"\n{'='*80}")
        print(f"📊 RESULTS")
        print(f"{'='*80}")
        print(f"✅ Successfully fixed: {success} images")
        print(f"❌ Failed: {failed} images")
        print(f"{'='*80}\n")
        
        if success > 0:
            print("✅ Facebook event images are now protected!")
            print("   Images are permanently stored on Supabase.\n")


if __name__ == "__main__":
    fix_facebook_images()

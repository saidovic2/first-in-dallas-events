"""
Protect Facebook events by caching images to Supabase
This prevents broken images if Facebook blocks the URLs
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from supabase import create_client, Client

load_dotenv()

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Get Railway database
DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not all([DATABASE_URL, SUPABASE_URL, SUPABASE_KEY]):
    print("❌ Missing environment variables!")
    exit(1)

engine = create_engine(DATABASE_URL)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*80)
print("🛡️  PROTECTING FACEBOOK EVENTS")
print("="*80)
print("\nThis will:")
print("1. Download Facebook event images")
print("2. Upload them to Supabase storage")
print("3. Update event records with Supabase URLs")
print("4. Protect against broken Facebook image links\n")

def upload_image_to_supabase(image_url, event_id):
    """Download and upload image to Supabase"""
    try:
        # Download image
        response = requests.get(image_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Generate filename
        file_extension = 'jpg'
        filename = f"facebook_events/{event_id}_{datetime.now().timestamp()}.{file_extension}"
        
        # Upload to Supabase
        result = supabase.storage.from_('event-images').upload(
            filename,
            response.content,
            file_options={"content-type": f"image/{file_extension}"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_('event-images').get_public_url(filename)
        
        return public_url
        
    except Exception as e:
        return None


def protect_facebook_events():
    """Cache Facebook event images to Supabase"""
    
    with engine.connect() as conn:
        # Get Facebook events with Facebook image URLs
        result = conn.execute(text("""
            SELECT id, title, image_url
            FROM events 
            WHERE source_type = 'FACEBOOK'
            AND image_url IS NOT NULL
            AND image_url LIKE '%facebook%'
            AND image_url NOT LIKE '%supabase%'
            ORDER BY id
        """))
        
        events = list(result)
        total = len(events)
        
        if total == 0:
            print("✅ All Facebook events already protected!\n")
            return
        
        print(f"📸 Found {total} Facebook events with Facebook-hosted images")
        print(f"   Caching them to Supabase storage...\n")
        
        success = 0
        failed = 0
        
        for i, event in enumerate(events, 1):
            try:
                print(f"[{i}/{total}] {event.title[:40]}... ", end="")
                
                # Upload to Supabase
                supabase_url = upload_image_to_supabase(event.image_url, event.id)
                
                if supabase_url:
                    # Update database
                    conn.execute(text("""
                        UPDATE events 
                        SET image_url = :new_url
                        WHERE id = :event_id
                    """), {"new_url": supabase_url, "event_id": event.id})
                    conn.commit()
                    
                    print(f"✅ Cached")
                    success += 1
                else:
                    print(f"❌ Failed")
                    failed += 1
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:40]}")
                failed += 1
                conn.rollback()
        
        print(f"\n{'='*80}")
        print(f"📊 PROTECTION SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Successfully cached: {success} images")
        print(f"❌ Failed: {failed} images")
        print(f"{'='*80}\n")
        
        if success > 0:
            print("✅ Facebook events are now protected!")
            print("   Images are cached on Supabase and won't break.\n")


def main():
    response = input("⚠️  This will cache all Facebook event images. Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Protection cancelled.\n")
        return
    
    protect_facebook_events()


if __name__ == "__main__":
    main()

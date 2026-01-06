"""
Upload category-based placeholder images to Supabase and fix Facebook events
Since Facebook blocks access to fbcdn.net URLs, we'll use quality placeholders
"""

import os
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from supabase import create_client, Client
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not all([DATABASE_URL, SUPABASE_URL, SUPABASE_KEY]):
    print("❌ Missing environment variables!")
    exit(1)

engine = create_engine(DATABASE_URL)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# High-quality placeholder images (Unsplash - already hosted)
CATEGORY_PLACEHOLDERS = {
    'Music & Concerts': 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=1200&q=85',
    'Entertainment': 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1200&q=85',
    'Arts & Culture': 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=1200&q=85',
    'Sports & Recreation': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=85',
    'Family & Kids': 'https://images.unsplash.com/photo-1502781252888-9143ba7f074e?w=1200&q=85',
    'Food & Dining': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=85',
    'Default': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&q=85'
}

print("="*80)
print("🛡️  FIXING FACEBOOK IMAGES WITH SUPABASE PLACEHOLDERS")
print("="*80)
print("\nFacebook blocks access to fbcdn.net images (403 Forbidden).")
print("This will upload placeholder images to Supabase and update events.\n")

def upload_placeholder_to_supabase(category, placeholder_url):
    """Download placeholder and upload to Supabase"""
    try:
        # Download placeholder image
        response = requests.get(placeholder_url, timeout=15)
        response.raise_for_status()
        
        # Create filename
        category_slug = category.lower().replace(' & ', '_').replace(' ', '_')
        filename = f"placeholders/{category_slug}.jpg"
        
        # Check if already exists
        try:
            existing = supabase.storage.from_('event-images').get_public_url(filename)
            if existing:
                return existing
        except:
            pass
        
        # Upload to Supabase
        supabase.storage.from_('event-images').upload(
            filename,
            response.content,
            file_options={"content-type": "image/jpeg", "upsert": "true"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_('event-images').get_public_url(filename)
        return public_url
        
    except Exception as e:
        print(f"⚠️  Failed to upload {category} placeholder: {str(e)[:50]}")
        return placeholder_url  # Fallback to direct Unsplash URL

def fix_facebook_images():
    """Fix Facebook event images with Supabase-hosted placeholders"""
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM events 
            WHERE source_type = 'FACEBOOK'
            AND image_url IS NOT NULL
            AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
            AND image_url NOT LIKE '%supabase%'
        """))
        
        broken_count = result.scalar()
        
        if broken_count == 0:
            print("✅ All Facebook events already fixed!\n")
            return
        
        print(f"📸 Found {broken_count} events with broken Facebook CDN URLs\n")
        print("Step 1: Uploading placeholder images to Supabase...\n")
        
        # Upload placeholders to Supabase
        supabase_placeholders = {}
        for category, url in CATEGORY_PLACEHOLDERS.items():
            print(f"  📤 Uploading {category} placeholder...", end=" ", flush=True)
            supabase_url = upload_placeholder_to_supabase(category, url)
            supabase_placeholders[category] = supabase_url
            print("✅")
        
        print(f"\n{'='*80}")
        print("Step 2: Updating events with Supabase URLs...\n")
        
        total_updated = 0
        
        for category, supabase_url in supabase_placeholders.items():
            if category == 'Default':
                # Update uncategorized events
                result = conn.execute(text("""
                    UPDATE events 
                    SET image_url = :placeholder
                    WHERE source_type = 'FACEBOOK'
                    AND image_url IS NOT NULL
                    AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
                    AND image_url NOT LIKE '%supabase%'
                    AND (category IS NULL OR category NOT IN :categories)
                """), {
                    "placeholder": supabase_url,
                    "categories": tuple(k for k in CATEGORY_PLACEHOLDERS.keys() if k != 'Default')
                })
            else:
                result = conn.execute(text("""
                    UPDATE events 
                    SET image_url = :placeholder
                    WHERE source_type = 'FACEBOOK'
                    AND image_url IS NOT NULL
                    AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
                    AND image_url NOT LIKE '%supabase%'
                    AND category = :category
                """), {"placeholder": supabase_url, "category": category})
            
            if result.rowcount > 0:
                print(f"  ✅ {category}: {result.rowcount} events")
                total_updated += result.rowcount
        
        conn.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ COMPLETE - Fixed {total_updated} events")
        print(f"{'='*80}")
        print(f"📍 Images are now hosted on Supabase")
        print(f"🔗 Permanent URLs that won't break\n")

if __name__ == "__main__":
    fix_facebook_images()

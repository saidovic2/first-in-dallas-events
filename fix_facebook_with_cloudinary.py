"""
Upload category-based placeholder images to Cloudinary and fix Facebook events
Since Facebook blocks access to fbcdn.net URLs (403 Forbidden), we use placeholders
"""

import os
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import cloudinary
import cloudinary.uploader
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

if not all([DATABASE_URL, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    print("❌ Missing environment variables!")
    print("\nPlease add to .env file:")
    print("CLOUDINARY_CLOUD_NAME=your_cloud_name")
    print("CLOUDINARY_API_KEY=your_api_key")
    print("CLOUDINARY_API_SECRET=your_api_secret")
    print("\nGet credentials from: https://cloudinary.com/console\n")
    exit(1)

engine = create_engine(DATABASE_URL)

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

# High-quality placeholder images (Unsplash)
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
print("☁️  FIXING FACEBOOK IMAGES WITH CLOUDINARY")
print("="*80)
print("\nFacebook blocks access to fbcdn.net images (403 Forbidden).")
print("Uploading placeholder images to Cloudinary...\n")

def upload_to_cloudinary(category, source_url):
    """Upload placeholder image to Cloudinary"""
    try:
        category_slug = category.lower().replace(' & ', '_').replace(' ', '_')
        public_id = f"event_placeholders/{category_slug}"
        
        # Upload to Cloudinary (fetches from URL directly)
        result = cloudinary.uploader.upload(
            source_url,
            public_id=public_id,
            overwrite=True,
            folder="event_placeholders",
            transformation=[
                {'width': 1200, 'height': 800, 'crop': 'fill', 'quality': 'auto:good'}
            ]
        )
        
        return result['secure_url']
        
    except Exception as e:
        print(f"⚠️  Failed to upload {category}: {str(e)[:60]}")
        return None

def fix_facebook_images():
    """Fix Facebook event images with Cloudinary-hosted placeholders"""
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM events 
            WHERE source_type = 'FACEBOOK'
            AND image_url IS NOT NULL
            AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
            AND image_url NOT LIKE '%cloudinary%'
        """))
        
        broken_count = result.scalar()
        
        if broken_count == 0:
            print("✅ All Facebook events already fixed!\n")
            return
        
        print(f"📸 Found {broken_count} events with broken Facebook CDN URLs\n")
        print("Step 1: Uploading placeholder images to Cloudinary...\n")
        
        # Upload placeholders to Cloudinary
        cloudinary_urls = {}
        for category, url in CATEGORY_PLACEHOLDERS.items():
            print(f"  ☁️  Uploading {category} placeholder...", end=" ", flush=True)
            cloudinary_url = upload_to_cloudinary(category, url)
            if cloudinary_url:
                cloudinary_urls[category] = cloudinary_url
                print("✅")
            else:
                print("❌ (using direct URL)")
                cloudinary_urls[category] = url
        
        print(f"\n{'='*80}")
        print("Step 2: Updating events with Cloudinary URLs...\n")
        
        total_updated = 0
        
        for category, cloudinary_url in cloudinary_urls.items():
            if category == 'Default':
                # Update uncategorized events
                result = conn.execute(text("""
                    UPDATE events 
                    SET image_url = :placeholder
                    WHERE source_type = 'FACEBOOK'
                    AND image_url IS NOT NULL
                    AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
                    AND image_url NOT LIKE '%cloudinary%'
                    AND (category IS NULL OR category NOT IN :categories)
                """), {
                    "placeholder": cloudinary_url,
                    "categories": tuple(k for k in CATEGORY_PLACEHOLDERS.keys() if k != 'Default')
                })
            else:
                result = conn.execute(text("""
                    UPDATE events 
                    SET image_url = :placeholder
                    WHERE source_type = 'FACEBOOK'
                    AND image_url IS NOT NULL
                    AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
                    AND image_url NOT LIKE '%cloudinary%'
                    AND category = :category
                """), {"placeholder": cloudinary_url, "category": category})
            
            if result.rowcount > 0:
                print(f"  ✅ {category}: {result.rowcount} events")
                total_updated += result.rowcount
        
        conn.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ COMPLETE - Fixed {total_updated} events")
        print(f"{'='*80}")
        print(f"☁️  Images are now hosted on Cloudinary")
        print(f"🔗 Permanent, optimized URLs that won't break\n")

if __name__ == "__main__":
    fix_facebook_images()

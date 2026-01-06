"""Test if we can access Facebook CDN images"""
import os
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 TESTING FACEBOOK IMAGE ACCESS")
print("="*80)

with engine.connect() as conn:
    # Get a few sample Facebook image URLs
    result = conn.execute(text("""
        SELECT id, title, image_url
        FROM events
        WHERE source_type = 'FACEBOOK'
        AND image_url IS NOT NULL
        AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
        LIMIT 5
    """))
    
    events = list(result)
    
    print(f"\nTesting access to {len(events)} sample images...\n")
    
    for event in events:
        print(f"Event {event.id}: {event.title[:50]}...")
        print(f"URL: {event.image_url[:80]}...")
        
        try:
            response = requests.head(event.image_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Accessible!\n")
            else:
                print(f"❌ Blocked (HTTP {response.status_code})\n")
        except Exception as e:
            print(f"❌ Error: {str(e)[:60]}\n")

print("="*80)
print("CONCLUSION:")
print("="*80)
print("If all images show 403 Forbidden, Facebook blocks external access.")
print("We cannot download these images to upload to Cloudinary.")
print("Recommendation: Use category-based placeholder images instead.\n")

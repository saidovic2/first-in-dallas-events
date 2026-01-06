"""
Fix broken Facebook event images by setting them to NULL
Facebook blocks external access to fbcdn.net URLs with 403 Forbidden
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔧 FIXING BROKEN FACEBOOK IMAGES")
print("="*80)
print("\nFacebook blocks external access to fbcdn.net image URLs.")
print("This script will remove broken image URLs so the frontend handles them gracefully.\n")

with engine.connect() as conn:
    # Check current status
    result = conn.execute(text("""
        SELECT COUNT(*) FROM events 
        WHERE source_type = 'FACEBOOK'
        AND image_url IS NOT NULL
        AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
        AND image_url NOT LIKE '%supabase%'
    """))
    
    broken_count = result.scalar()
    
    if broken_count == 0:
        print("✅ No broken Facebook image URLs found!\n")
        exit(0)
    
    print(f"📸 Found {broken_count} events with broken Facebook CDN URLs\n")
    
    choice = input("Choose an option:\n"
                   "1. Set broken image URLs to NULL (recommended)\n"
                   "2. Keep broken URLs (images will fail to load)\n"
                   "3. Cancel\n"
                   "Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🔄 Removing broken image URLs...")
        
        result = conn.execute(text("""
            UPDATE events 
            SET image_url = NULL
            WHERE source_type = 'FACEBOOK'
            AND image_url IS NOT NULL
            AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
            AND image_url NOT LIKE '%supabase%'
        """))
        
        conn.commit()
        
        print(f"✅ Updated {result.rowcount} events")
        print("\n📝 Note: Events will now use fallback images in the frontend")
        print("   Consider adding placeholder images or re-scraping from other sources.\n")
        
    elif choice == "2":
        print("\n⚠️  Keeping broken URLs. Images will fail to load in the frontend.\n")
    else:
        print("\n❌ Cancelled.\n")

print("="*80)

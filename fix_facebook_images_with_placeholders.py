"""
Fix broken Facebook event images with category-based placeholder images
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

# Unsplash placeholder images by category (high quality, royalty-free)
CATEGORY_PLACEHOLDERS = {
    'Music & Concerts': 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&q=80',
    'Entertainment': 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&q=80',
    'Arts & Culture': 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=800&q=80',
    'Sports & Recreation': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',
    'Family & Kids': 'https://images.unsplash.com/photo-1502781252888-9143ba7f074e?w=800&q=80',
    'Food & Dining': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&q=80',
    'Default': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&q=80'
}

print("="*80)
print("🎨 FIXING FACEBOOK IMAGES WITH PLACEHOLDERS")
print("="*80)
print("\nThis will replace broken Facebook CDN URLs with category-based")
print("placeholder images from Unsplash (high quality, royalty-free).\n")

with engine.connect() as conn:
    # Check broken images
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
                   "1. Use category-based placeholder images (recommended)\n"
                   "2. Set image URLs to NULL (no images)\n"
                   "3. Cancel\n"
                   "Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🎨 Applying placeholder images based on categories...")
        
        updated = 0
        
        for category, placeholder_url in CATEGORY_PLACEHOLDERS.items():
            if category == 'Default':
                # Update events with no category or unmatched categories
                result = conn.execute(text("""
                    UPDATE events 
                    SET image_url = :placeholder
                    WHERE source_type = 'FACEBOOK'
                    AND image_url IS NOT NULL
                    AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
                    AND image_url NOT LIKE '%supabase%'
                    AND (category IS NULL OR category NOT IN :categories)
                """), {
                    "placeholder": placeholder_url,
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
                """), {"placeholder": placeholder_url, "category": category})
            
            if result.rowcount > 0:
                print(f"  ✅ {category}: {result.rowcount} events")
                updated += result.rowcount
        
        conn.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ Updated {updated} events with placeholder images")
        print(f"{'='*80}\n")
        
    elif choice == "2":
        print("\n🔄 Setting broken image URLs to NULL...")
        
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
        print(f"\n📝 Note: Events will display without images.\n")
        
    else:
        print("\n❌ Cancelled.\n")

print("="*80)

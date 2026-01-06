"""Check current status of Facebook event images"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 CHECKING FACEBOOK EVENT IMAGES")
print("="*80)

with engine.connect() as conn:
    # Count total Facebook events
    result = conn.execute(text("SELECT COUNT(*) FROM events WHERE source_type = 'FACEBOOK'"))
    total = result.scalar()
    print(f"\n📊 Total Facebook events: {total}")
    
    # Count events with images
    result = conn.execute(text("""
        SELECT COUNT(*) FROM events 
        WHERE source_type = 'FACEBOOK' 
        AND image_url IS NOT NULL
    """))
    with_images = result.scalar()
    print(f"📸 Facebook events with image_url: {with_images}")
    
    # Count events without images
    result = conn.execute(text("""
        SELECT COUNT(*) FROM events 
        WHERE source_type = 'FACEBOOK' 
        AND image_url IS NULL
    """))
    without_images = result.scalar()
    print(f"❌ Facebook events WITHOUT image_url: {without_images}")
    
    # Check image URL patterns
    print(f"\n{'='*80}")
    print("🔗 IMAGE URL PATTERNS:")
    print("="*80)
    
    result = conn.execute(text("""
        SELECT 
            CASE 
                WHEN image_url IS NULL THEN 'NULL'
                WHEN image_url LIKE '%supabase%' THEN 'Supabase (Protected)'
                WHEN image_url LIKE '%facebook%' THEN 'Facebook (Unprotected)'
                WHEN image_url LIKE '%fbcdn%' THEN 'Facebook CDN (Unprotected)'
                ELSE 'Other'
            END as url_type,
            COUNT(*) as count
        FROM events
        WHERE source_type = 'FACEBOOK'
        GROUP BY url_type
        ORDER BY count DESC
    """))
    
    for row in result:
        print(f"   {row.url_type}: {row.count} events")
    
    # Sample some image URLs
    print(f"\n{'='*80}")
    print("📋 SAMPLE IMAGE URLs (first 10):")
    print("="*80)
    
    result = conn.execute(text("""
        SELECT id, title, image_url
        FROM events
        WHERE source_type = 'FACEBOOK'
        ORDER BY id DESC
        LIMIT 10
    """))
    
    for row in result:
        title = row.title[:40] + "..." if len(row.title) > 40 else row.title
        img_status = "NULL" if row.image_url is None else row.image_url[:80] + "..."
        print(f"\n   ID {row.id}: {title}")
        print(f"   Image: {img_status}")

print(f"\n{'='*80}\n")

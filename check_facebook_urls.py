"""Check Facebook event URLs for proxy issues"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("🔍 Checking Facebook event URLs...\n")

with engine.connect() as conn:
    # Get sample Facebook events
    result = conn.execute(text("""
        SELECT id, title, source_url, status
        FROM events 
        WHERE source_type = 'FACEBOOK'
        ORDER BY id DESC
        LIMIT 10
    """))
    
    print("📋 Sample Facebook Event URLs:")
    print("="*80)
    
    proxied_count = 0
    working_count = 0
    
    for row in result:
        url = row.source_url
        is_proxied = 'l.facebook.com' in url or '/l.php' in url
        
        status = "⚠️  PROXIED" if is_proxied else "✅ DIRECT"
        
        if is_proxied:
            proxied_count += 1
        else:
            working_count += 1
        
        print(f"\n{status}")
        print(f"ID: {row.id}")
        print(f"Title: {row.title[:50]}")
        print(f"URL: {url[:80]}")
    
    print(f"\n{'='*80}")
    print(f"📊 Summary:")
    print(f"   ✅ Direct Facebook URLs: {working_count}")
    print(f"   ⚠️  Proxied URLs: {proxied_count}")
    print(f"{'='*80}\n")
    
    if proxied_count > 0:
        print("⚠️  WARNING: Some URLs are proxied!")
        print("   These may become non-clickable over time.")
        print("   Solution: Use direct Facebook event URLs (facebook.com/events/...)")

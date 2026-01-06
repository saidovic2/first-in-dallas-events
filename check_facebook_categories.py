"""Check Facebook event categories"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT category, COUNT(*) as count
        FROM events
        WHERE source_type = 'FACEBOOK'
        AND image_url IS NOT NULL
        AND (image_url LIKE '%facebook%' OR image_url LIKE '%fbcdn%')
        AND image_url NOT LIKE '%supabase%'
        GROUP BY category
        ORDER BY count DESC
    """))
    
    print("\n📊 Facebook Events by Category (with broken images):\n")
    total = 0
    for row in result:
        cat = row.category if row.category else "No Category"
        print(f"   {cat}: {row.count} events")
        total += row.count
    
    print(f"\n   TOTAL: {total} events\n")

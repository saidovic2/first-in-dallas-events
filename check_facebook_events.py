"""Quick check for Facebook events in database"""
import os
from sqlalchemy import create_engine, text

# Get DATABASE_URL from environment
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check Facebook events
    result = conn.execute(text("SELECT COUNT(*) FROM events WHERE source_type = 'FACEBOOK'"))
    facebook_count = result.scalar()
    print(f"✅ Facebook events in database: {facebook_count}")
    
    # Check Draft events
    result = conn.execute(text("SELECT COUNT(*) FROM events WHERE status = 'DRAFT'"))
    draft_count = result.scalar()
    print(f"📝 Draft events in database: {draft_count}")
    
    # Check all events
    result = conn.execute(text("SELECT COUNT(*) FROM events"))
    total_count = result.scalar()
    print(f"📊 Total events in database: {total_count}")
    
    # Check recent Facebook events
    result = conn.execute(text("""
        SELECT id, title, status, source_type, created_at 
        FROM events 
        WHERE source_type = 'FACEBOOK' 
        ORDER BY created_at DESC 
        LIMIT 5
    """))
    
    print(f"\n📋 Recent Facebook events:")
    for row in result:
        print(f"   ID: {row.id} | {row.title[:50]} | Status: {row.status}")

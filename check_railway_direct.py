"""Check Railway database directly"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Connecting to: {DATABASE_URL[:60]}...\n")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check highest ID
    result = conn.execute(text("SELECT MAX(id) as max_id FROM events"))
    max_id = result.scalar()
    print(f"📊 Highest event ID in database: {max_id}")
    
    # Check total
    result = conn.execute(text("SELECT COUNT(*) FROM events"))
    total = result.scalar()
    print(f"📊 Total events: {total}")
    
    # Check events with ID > 2800
    result = conn.execute(text("SELECT COUNT(*) FROM events WHERE id > 2800"))
    high_id_count = result.scalar()
    print(f"📊 Events with ID > 2800: {high_id_count}")
    
    # Check by source
    result = conn.execute(text("""
        SELECT source_type, COUNT(*) as count 
        FROM events 
        GROUP BY source_type 
        ORDER BY count DESC
    """))
    print(f"\n📋 Events by source:")
    for row in result:
        print(f"   {row.source_type}: {row.count}")
    
    # Check last 5 events
    result = conn.execute(text("""
        SELECT id, title, source_type, status, created_at 
        FROM events 
        ORDER BY id DESC 
        LIMIT 5
    """))
    print(f"\n📋 Last 5 events (by ID):")
    for row in result:
        print(f"   ID: {row.id} | {row.source_type} | {row.status}")

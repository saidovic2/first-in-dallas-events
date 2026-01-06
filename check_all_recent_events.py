"""Check all recent events in database"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check total counts
    result = conn.execute(text("SELECT COUNT(*) FROM events"))
    total = result.scalar()
    print(f"📊 Total events: {total}")
    
    # Check by status
    result = conn.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM events 
        GROUP BY status
    """))
    print(f"\n📋 Events by status:")
    for row in result:
        print(f"   {row.status}: {row.count}")
    
    # Check by source_type
    result = conn.execute(text("""
        SELECT source_type, COUNT(*) as count 
        FROM events 
        GROUP BY source_type
        ORDER BY count DESC
    """))
    print(f"\n📋 Events by source:")
    for row in result:
        print(f"   {row.source_type}: {row.count}")
    
    # Check recent 10 events
    result = conn.execute(text("""
        SELECT id, title, source_type, status, created_at 
        FROM events 
        ORDER BY id DESC 
        LIMIT 10
    """))
    print(f"\n📋 10 Most recent events:")
    for row in result:
        print(f"   ID: {row.id} | {row.source_type} | {row.status} | {row.title[:40]}")

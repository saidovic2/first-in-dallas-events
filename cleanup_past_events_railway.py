"""
Delete past events from Railway database (Dallas timezone)
KEEPS today's events - only deletes events from yesterday and before
"""

import os
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL or 'localhost' in DATABASE_URL:
    print("❌ ERROR: Must use Railway DATABASE_URL!")
    print(f"   Current: {DATABASE_URL}")
    exit(1)

print("="*80)
print("🧹 CLEANUP PAST EVENTS FROM RAILWAY DATABASE")
print("="*80)
print("\n✅ Using Dallas timezone (America/Chicago)")
print("✅ Keeps events happening TODAY")
print("❌ Deletes events from the past (before today)\n")

# Create connection
engine = create_engine(DATABASE_URL)

# Get Dallas timezone
dallas_tz = pytz_timezone('America/Chicago')
now_dallas = datetime.now(dallas_tz)

# Start of today in Dallas
today_start = now_dallas.replace(hour=0, minute=0, second=0, microsecond=0)

print(f"📅 Current Dallas time: {now_dallas.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"📅 Today starts at: {today_start.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   (Will keep all events from this time onwards)\n")

with engine.connect() as conn:
    # Count past events
    result = conn.execute(text("""
        SELECT COUNT(*) 
        FROM events 
        WHERE start_at < :cutoff_time
    """), {"cutoff_time": today_start})
    
    count = result.scalar()
    
    if count == 0:
        print("✅ No past events found! Database is clean.\n")
        exit(0)
    
    print(f"📊 Found {count} past events to delete\n")
    
    # Show sample events that will be deleted
    result = conn.execute(text("""
        SELECT id, title, start_at, source_type 
        FROM events 
        WHERE start_at < :cutoff_time
        ORDER BY start_at DESC
        LIMIT 10
    """), {"cutoff_time": today_start})
    
    print("📋 Sample events to be deleted:")
    print("="*80)
    
    for row in result:
        event_date = row.start_at.astimezone(dallas_tz)
        print(f"   ID: {row.id} | {row.source_type} | {event_date.strftime('%Y-%m-%d')} | {row.title[:50]}")
    
    if count > 10:
        print(f"   ... and {count - 10} more events")
    
    print(f"\n{'='*80}")
    print(f"⚠️  WARNING: This will DELETE {count} events from Railway database!")
    print(f"{'='*80}\n")
    
    response = input("Type 'DELETE' to proceed (or anything else to cancel): ").strip()
    
    if response == 'DELETE':
        print(f"\n🗑️  Deleting {count} past events...")
        
        # Delete past events
        result = conn.execute(text("""
            DELETE FROM events 
            WHERE start_at < :cutoff_time
        """), {"cutoff_time": today_start})
        
        conn.commit()
        
        deleted = result.rowcount
        
        print(f"✅ Successfully deleted {deleted} past events!")
        
        # Check remaining events
        result = conn.execute(text("SELECT COUNT(*) FROM events"))
        remaining = result.scalar()
        
        print(f"\n📊 Database status:")
        print(f"   ✅ Remaining events: {remaining}")
        print(f"   🗑️  Deleted events: {deleted}")
        print(f"\n🎉 Cleanup complete! Only upcoming events remain.\n")
        
    else:
        print("\n❌ Cleanup cancelled. No events were deleted.\n")

"""Check event dates to see why they're not showing"""
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        now = datetime.now(timezone.utc)
        print(f"Current time (UTC): {now}")
        print(f"\nChecking Ticketmaster events:\n")
        
        # Get all Ticketmaster events with their dates
        result = conn.execute(text("""
            SELECT id, title, start_at, status, city
            FROM events 
            WHERE source_type = 'TICKETMASTER'
            ORDER BY start_at ASC
            LIMIT 20
        """))
        
        future_count = 0
        past_count = 0
        
        for row in result:
            event_id, title, start_at, status, city = row
            is_future = start_at > now if start_at.tzinfo else True
            
            symbol = "✓" if is_future else "✗"
            future_count += 1 if is_future else 0
            past_count += 0 if is_future else 1
            
            print(f"{symbol} [{event_id}] {title[:40]}")
            print(f"   Date: {start_at} | Status: {status} | City: {city}")
            print(f"   Has timezone: {start_at.tzinfo is not None}")
            print()
        
        print(f"\n{'='*60}")
        print(f"Future events: {future_count}")
        print(f"Past events: {past_count}")
        
        # Check if events have timezone info
        result = conn.execute(text("""
            SELECT 
                COUNT(*) FILTER (WHERE start_at::text ~ '\+') as with_tz,
                COUNT(*) FILTER (WHERE start_at::text !~ '\+') as without_tz
            FROM events 
            WHERE source_type = 'TICKETMASTER'
        """))
        
        row = result.fetchone()
        print(f"\nTimezone info:")
        print(f"  With timezone: {row[0]}")
        print(f"  Without timezone: {row[1]}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

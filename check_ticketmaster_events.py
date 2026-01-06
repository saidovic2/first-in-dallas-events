"""
Quick script to check if Ticketmaster events are in database
"""
from sqlalchemy import create_engine, text

# Railway database connection
DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check total events
        result = conn.execute(text("SELECT COUNT(*) as count FROM events"))
        total = result.fetchone()[0]
        print(f"📊 Total events in database: {total}")
        
        # Check Ticketmaster events
        result = conn.execute(text("SELECT COUNT(*) as count FROM events WHERE source_type = 'TICKETMASTER'"))
        ticketmaster = result.fetchone()[0]
        print(f"🎫 Ticketmaster events: {ticketmaster}")
        
        # Check DRAFT events
        result = conn.execute(text("SELECT COUNT(*) as count FROM events WHERE status = 'DRAFT'"))
        draft = result.fetchone()[0]
        print(f"📝 DRAFT events: {draft}")
        
        # Show recent Ticketmaster events if any
        if ticketmaster > 0:
            print(f"\n🎯 Recent Ticketmaster Events:")
            result = conn.execute(text("""
                SELECT id, title, city, start_at::date, status 
                FROM events 
                WHERE source_type = 'TICKETMASTER' 
                ORDER BY created_at DESC 
                LIMIT 10
            """))
            
            for row in result:
                print(f"   [{row[0]}] {row[1][:50]} | {row[2]} | {row[3]} | {row[4]}")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("\n💡 Try checking your Railway/Supabase dashboard for the correct DATABASE_URL")

"""
Delete All Ticketmaster Events
Safely removes all events with source_type = 'TICKETMASTER'
"""

from sqlalchemy import create_engine, text
from datetime import datetime

DATABASE_URL = 'postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway'

try:
    print("\n" + "="*80)
    print("DELETE TICKETMASTER EVENTS")
    print("="*80 + "\n")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # First, count how many events will be deleted
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM events
            WHERE source_type = 'TICKETMASTER'
        """))
        
        count = result.fetchone()[0]
        
        if count == 0:
            print("No Ticketmaster events found in database.")
            exit(0)
        
        print(f"Found {count} Ticketmaster events to delete.\n")
        
        # Show some sample events
        sample_result = conn.execute(text("""
            SELECT id, title, city, start_at
            FROM events
            WHERE source_type = 'TICKETMASTER'
            ORDER BY id
            LIMIT 10
        """))
        
        print("Sample events to be deleted:")
        print("-" * 80)
        for event_id, title, city, start_at in sample_result:
            print(f"  [{event_id}] {title[:50]} | {city} | {start_at}")
        
        if count > 10:
            print(f"  ... and {count - 10} more events")
        
        print("-" * 80)
        
        # Ask for confirmation
        print(f"\n⚠️  WARNING: This will permanently delete {count} Ticketmaster events!")
        response = input(f"\nType 'DELETE' to confirm: ").strip()
        
        if response != 'DELETE':
            print("\n✓ Cancelled - No events deleted.")
            exit(0)
        
        print(f"\nDeleting {count} events...")
        
        # Delete all Ticketmaster events
        delete_result = conn.execute(text("""
            DELETE FROM events
            WHERE source_type = 'TICKETMASTER'
        """))
        
        conn.commit()
        
        deleted_count = delete_result.rowcount
        
        print(f"\n{'='*80}")
        print(f"DELETION COMPLETE")
        print(f"{'='*80}")
        print(f"✓ Deleted: {deleted_count} Ticketmaster events")
        print(f"{'='*80}\n")
        
        print("✓ Database cleaned!")
        print("✓ Ready for new Apify import from better actor!")
        
        # Show remaining events count
        remaining = conn.execute(text("SELECT COUNT(*) FROM events")).fetchone()[0]
        print(f"\n→ Remaining events in database: {remaining}")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

"""
Delete All Ticketmaster Events - Auto version
Run this after user confirms
"""

from sqlalchemy import create_engine, text

DATABASE_URL = 'postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway'

print("\n" + "="*80)
print("DELETE TICKETMASTER EVENTS")
print("="*80 + "\n")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Count
    result = conn.execute(text("""
        SELECT COUNT(*) as count
        FROM events
        WHERE source_type = 'TICKETMASTER'
    """))
    
    count = result.fetchone()[0]
    
    print(f"Found {count} Ticketmaster events")
    
    if count == 0:
        print("✓ No Ticketmaster events to delete.")
    else:
        # Show samples
        samples = conn.execute(text("""
            SELECT id, title, city
            FROM events
            WHERE source_type = 'TICKETMASTER'
            ORDER BY id
            LIMIT 5
        """)).fetchall()
        
        print(f"\nSample events:")
        for event_id, title, city in samples:
            print(f"  [{event_id}] {title[:50]} | {city}")
        
        if count > 5:
            print(f"  ... and {count - 5} more")
        
        # Delete
        print(f"\nDeleting {count} events...")
        
        conn.execute(text("""
            DELETE FROM events
            WHERE source_type = 'TICKETMASTER'
        """))
        
        conn.commit()
        
        print(f"\n{'='*80}")
        print(f"✓ DELETED: {count} Ticketmaster events")
        print(f"{'='*80}\n")
        
        # Show remaining
        remaining = conn.execute(text("SELECT COUNT(*) FROM events")).fetchone()[0]
        print(f"→ Remaining events: {remaining}")
        print(f"✓ Ready for new Apify import!")

print()

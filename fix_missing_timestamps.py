"""Fix missing created_at and updated_at timestamps"""
from sqlalchemy import create_engine, text
from datetime import datetime, timezone

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check events with NULL timestamps
        result = conn.execute(text("""
            SELECT COUNT(*) FROM events 
            WHERE created_at IS NULL OR updated_at IS NULL
        """))
        
        null_count = result.fetchone()[0]
        print(f"Events with NULL timestamps: {null_count}")
        
        if null_count > 0:
            print(f"\nFixing {null_count} events...")
            
            # Set created_at and updated_at for all NULL events
            now = datetime.now(timezone.utc)
            
            result = conn.execute(text("""
                UPDATE events
                SET 
                    created_at = COALESCE(created_at, :now),
                    updated_at = COALESCE(updated_at, :now)
                WHERE created_at IS NULL OR updated_at IS NULL
                RETURNING id
            """), {"now": now})
            
            updated_ids = [row[0] for row in result]
            
            conn.commit()
            
            print(f"✓ Fixed {len(updated_ids)} events")
            print(f"  Set timestamps to: {now}")
            
            # Verify
            result = conn.execute(text("""
                SELECT COUNT(*) FROM events 
                WHERE created_at IS NULL OR updated_at IS NULL
            """))
            
            remaining = result.fetchone()[0]
            print(f"\nRemaining NULL timestamps: {remaining}")
            
            if remaining == 0:
                print("✓ All events now have timestamps!")
        else:
            print("✓ All events already have timestamps!")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

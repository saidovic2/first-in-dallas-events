import psycopg2
import os

# Railway database connection
DATABASE_URL = "postgresql://postgres:fXfexgCmIiwmHkiBgQsUAXgvhSCqgLrd@junction.proxy.rlwy.net:35793/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Count total events
    cursor.execute("SELECT COUNT(*) FROM events;")
    total = cursor.fetchone()[0]
    print(f"✅ Total events in database: {total}")
    
    # Count by status
    cursor.execute("SELECT status, COUNT(*) FROM events GROUP BY status;")
    status_counts = cursor.fetchall()
    print(f"\n📊 Events by status:")
    for status, count in status_counts:
        print(f"  - {status}: {count}")
    
    # Show recent events
    cursor.execute("SELECT title, status, created_at FROM events ORDER BY created_at DESC LIMIT 5;")
    recent = cursor.fetchall()
    print(f"\n📝 Recent events:")
    for title, status, created_at in recent:
        print(f"  - [{status}] {title[:50]}... ({created_at})")
    
    cursor.close()
    conn.close()
    print(f"\n✅ Database check complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")

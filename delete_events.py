import psycopg2

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check how many events exist
    cursor.execute("SELECT COUNT(*) FROM events;")
    count_before = cursor.fetchone()[0]
    print(f"📊 Events in database: {count_before}")
    
    if count_before == 0:
        print("✅ Database is already empty!")
    else:
        print(f"Deleting {count_before} events...")
        cursor.execute("DELETE FROM events;")
        conn.commit()
        
        # Verify deletion
        cursor.execute("SELECT COUNT(*) FROM events;")
        count_after = cursor.fetchone()[0]
        print(f"✅ Deleted! Remaining events: {count_after}")
        print("Now go to dashboard and sync Eventbrite again.")
        print("The new events will have categories!")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()

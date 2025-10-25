import psycopg2

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("Adding missing ENUM values...")
    
    # Add lowercase 'eventbrite' to sourcetype ENUM
    try:
        cursor.execute("ALTER TYPE sourcetype ADD VALUE IF NOT EXISTS 'eventbrite';")
        print("✅ Added 'eventbrite' to sourcetype")
    except Exception as e:
        print(f"⚠️ Could not add 'eventbrite': {e}")
    
    # Add lowercase 'facebook' to sourcetype ENUM
    try:
        cursor.execute("ALTER TYPE sourcetype ADD VALUE IF NOT EXISTS 'facebook';")
        print("✅ Added 'facebook' to sourcetype")
    except Exception as e:
        print(f"⚠️ Could not add 'facebook': {e}")
    
    conn.commit()
    print("\n🎉 ENUM values updated!")
    print("Now restart the worker and sync again.")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()

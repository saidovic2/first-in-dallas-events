import psycopg2
import os

# Get database URL from Railway
DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Drop tables
    print("Dropping events table...")
    cursor.execute("DROP TABLE IF EXISTS events CASCADE;")
    
    print("Dropping tasks table...")
    cursor.execute("DROP TABLE IF EXISTS tasks CASCADE;")
    
    # Commit changes
    conn.commit()
    
    print("✅ Tables dropped successfully!")
    print("Now restart the API on Railway and sync again.")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()

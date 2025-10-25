import psycopg2
import sys

# Railway production database URL
DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("Creating ENUM types...")
    
    # Create ENUM types (only if they don't exist)
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE pricetier AS ENUM ('FREE', 'PAID', 'DONATION');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    print("✅ pricetier ENUM created")
    
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE sourcetype AS ENUM (
                'FACEBOOK', 'FACEBOOK_BULK', 'EVENTBRITE', 'EVENTBRITE_BULK',
                'INSTAGRAM', 'WEBPAGE', 'ICS', 'RSS', 'MANUAL',
                'facebook_bulk', 'eventbrite', 'eventbrite_bulk'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    print("✅ sourcetype ENUM created")
    
    cursor.execute("""
        DO $$ BEGIN
            CREATE TYPE eventstatus AS ENUM ('DRAFT', 'PUBLISHED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    print("✅ eventstatus ENUM created")
    
    conn.commit()
    print("\n🎉 All ENUM types created successfully!")
    print("Now restart the API and worker on Railway, then sync again.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
finally:
    if conn:
        cursor.close()
        conn.close()

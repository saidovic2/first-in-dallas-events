"""
Add dallas_arboretum to sourcetype enum - Direct Railway Connection
"""
import psycopg2
from psycopg2 import sql

# Railway PostgreSQL connection
DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@postgres.railway.internal:5432/railway"

print("🔗 Connecting to Railway PostgreSQL...")

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("✅ Connected to database")
    
    # Add the new enum value
    print("\n📝 Adding 'dallas_arboretum' to sourcetype enum...")
    
    try:
        cursor.execute("ALTER TYPE sourcetype ADD VALUE 'dallas_arboretum'")
        print("✅ Successfully added 'dallas_arboretum' to sourcetype enum")
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️  'dallas_arboretum' already exists in sourcetype enum")
        else:
            raise e
    
    # Verify the change
    print("\n📋 Current sourcetype enum values:")
    cursor.execute("SELECT unnest(enum_range(NULL::sourcetype))::text")
    for row in cursor.fetchall():
        print(f"   - {row[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("\n🎉 You can now run the Dallas Arboretum sync from the CMS dashboard!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nNote: If you see 'postgres.railway.internal' connection error,")
    print("this script needs to run FROM Railway (not locally).")
    exit(1)

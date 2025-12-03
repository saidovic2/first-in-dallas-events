"""
Add dallas_arboretum to sourcetype enum - Railway External Connection
"""
import psycopg2

# Railway PostgreSQL external connection
DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

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
        error_msg = str(e)
        if "already exists" in error_msg:
            print("ℹ️  'dallas_arboretum' already exists in sourcetype enum")
        else:
            print(f"⚠️  Error: {error_msg}")
    
    # Verify the change
    print("\n📋 Current sourcetype enum values:")
    cursor.execute("SELECT unnest(enum_range(NULL::sourcetype))::text ORDER BY 1")
    values = cursor.fetchall()
    for row in values:
        marker = "✨" if row[0] == "dallas_arboretum" else "  "
        print(f"   {marker} {row[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Migration completed successfully!")
    print("\n🎉 You can now run the Dallas Arboretum sync from the CMS dashboard!")
    print("   Go to: Dashboard → Sync → Click '🌸 Sync Dallas Arboretum'")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("- Make sure psycopg2 is installed: pip install psycopg2-binary")
    print("- Check if the DATABASE_URL is correct")
    exit(1)

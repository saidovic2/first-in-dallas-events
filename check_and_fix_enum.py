"""
Check current enum values and add DALLAS_ARBORETUM properly
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

print("🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print("✅ Connected\n")

# Check current enum values
print("📋 Current sourcetype enum values:")
cursor.execute("SELECT unnest(enum_range(NULL::sourcetype))::text ORDER BY 1")
values = cursor.fetchall()
for row in values:
    print(f"   - {row[0]}")

print("\n🔧 Adding DALLAS_ARBORETUM (uppercase)...")

try:
    # Try to add the enum value (both cases to be safe)
    try:
        cursor.execute("ALTER TYPE sourcetype ADD VALUE 'DALLAS_ARBORETUM'")
        print("✅ Added DALLAS_ARBORETUM (uppercase)")
    except Exception as e:
        if "already exists" in str(e):
            print("ℹ️  DALLAS_ARBORETUM already exists")
        else:
            print(f"⚠️  Error adding DALLAS_ARBORETUM: {e}")
    
    # Verify
    print("\n📋 Updated enum values:")
    cursor.execute("SELECT unnest(enum_range(NULL::sourcetype))::text ORDER BY 1")
    values = cursor.fetchall()
    
    has_dallas = False
    for row in values:
        marker = "✨" if 'DALLAS' in row[0].upper() else "  "
        print(f"{marker} {row[0]}")
        if 'DALLAS' in row[0].upper():
            has_dallas = True
    
    if has_dallas:
        print("\n✅ Dallas Arboretum enum value successfully added!")
        
        # Now update the extractor to use uppercase
        print("\n⚠️  NOTE: The extractor needs to use 'DALLAS_ARBORETUM' (uppercase)")
    else:
        print("\n❌ Dallas Arboretum enum value NOT found")
        
except Exception as e:
    print(f"❌ Error: {e}")

cursor.close()
conn.close()

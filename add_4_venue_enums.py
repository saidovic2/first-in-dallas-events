"""
Add 4 new venue source types to enum
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

print("🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print("✅ Connected\n")

venues = [
    'PEROT_MUSEUM',
    'DALLAS_LIBRARY',
    'DALLAS_ZOO',
    'FAIR_PARK'
]

print("🔧 Adding venue enums to sourcetype...")

for venue in venues:
    try:
        cursor.execute(f"ALTER TYPE sourcetype ADD VALUE '{venue}'")
        print(f"✅ Added {venue}")
    except Exception as e:
        if "already exists" in str(e):
            print(f"ℹ️  {venue} already exists")
        else:
            print(f"⚠️  Error adding {venue}: {e}")

# Verify
print("\n📋 Current sourcetype enum values:")
cursor.execute("SELECT unnest(enum_range(NULL::sourcetype))::text ORDER BY 1")
values = cursor.fetchall()

for row in values:
    marker = "✨" if any(v in row[0] for v in ['PEROT', 'LIBRARY', 'ZOO', 'FAIR']) else "  "
    print(f"{marker} {row[0]}")

cursor.close()
conn.close()

print("\n✅ Database updated with all 4 venue enums!")

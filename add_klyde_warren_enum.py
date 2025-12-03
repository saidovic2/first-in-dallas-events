"""
Add KLYDE_WARREN_PARK to sourcetype enum
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

print("🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print("✅ Connected\n")

print("🔧 Adding KLYDE_WARREN_PARK to sourcetype enum...")

try:
    cursor.execute("ALTER TYPE sourcetype ADD VALUE 'KLYDE_WARREN_PARK'")
    print("✅ Added KLYDE_WARREN_PARK")
except Exception as e:
    if "already exists" in str(e):
        print("ℹ️  KLYDE_WARREN_PARK already exists")
    else:
        print(f"⚠️  Error: {e}")

# Verify
print("\n📋 Current sourcetype enum values:")
cursor.execute("SELECT unnest(enum_range(NULL::sourcetype))::text ORDER BY 1")
values = cursor.fetchall()

for row in values:
    marker = "✨" if 'KLYDE' in row[0].upper() else "  "
    print(f"{marker} {row[0]}")

cursor.close()
conn.close()

print("\n✅ Database updated!")

"""
Fix Dallas Arboretum image URLs - remove trailing ?
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

print("🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print("✅ Connected\n")

# Fix Dallas Arboretum image URLs
print("🔧 Fixing image URLs for Dallas Arboretum events...")

cursor.execute("""
    UPDATE events 
    SET image_url = RTRIM(image_url, '?')
    WHERE source_type = 'dallas_arboretum' 
    AND image_url LIKE '%?'
    RETURNING id, title, image_url
""")

fixed_events = cursor.fetchall()

print(f"✅ Fixed {len(fixed_events)} event image URLs\n")

for event in fixed_events:
    event_id, title, image_url = event
    print(f"✅ {title[:40]}")
    print(f"   New URL: {image_url}")
    print()

print("\n🎉 All image URLs fixed!")
print("Refresh your CMS dashboard and images should now appear!")

cursor.close()
conn.close()

"""
Check image URLs for Dallas Arboretum events
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

print("🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("✅ Connected\n")

# Get Dallas Arboretum events
print("📋 Dallas Arboretum Events Image URLs:\n")
cursor.execute("""
    SELECT 
        id,
        title,
        image_url,
        source_type
    FROM events 
    WHERE source_type = 'dallas_arboretum'
    ORDER BY created_at DESC
    LIMIT 10
""")

events = cursor.fetchall()

for event in events:
    event_id, title, image_url, source = event
    print(f"ID: {event_id}")
    print(f"Title: {title[:50]}")
    print(f"Image URL: {image_url}")
    print(f"Source: {source}")
    print("-" * 80)
    print()

# Test if images are accessible
print("\n🧪 Testing image accessibility...")
import requests

for event in events[:3]:  # Test first 3
    event_id, title, image_url, source = event
    if image_url:
        try:
            response = requests.head(image_url, timeout=5)
            status = "✅ Accessible" if response.status_code == 200 else f"❌ Error {response.status_code}"
            print(f"{title[:40]}: {status}")
        except Exception as e:
            print(f"{title[:40]}: ❌ {str(e)[:50]}")

cursor.close()
conn.close()

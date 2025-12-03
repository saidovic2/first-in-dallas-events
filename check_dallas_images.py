"""
Check Dallas Arboretum event image URLs and test if they're accessible
"""
import psycopg2
import requests

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

print("🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("✅ Connected\n")

# Get Dallas Arboretum events with their images
print("📋 Dallas Arboretum Events:\n")
cursor.execute("""
    SELECT 
        id,
        title,
        image_url,
        status
    FROM events 
    WHERE source_type = 'DALLAS_ARBORETUM'
    ORDER BY id DESC
    LIMIT 10
""")

events = cursor.fetchall()

if not events:
    print("❌ No Dallas Arboretum events found!")
    cursor.close()
    conn.close()
    exit(1)

print(f"Found {len(events)} Dallas Arboretum events\n")

for event in events:
    event_id, title, image_url, status = event
    print(f"{'='*80}")
    print(f"ID: {event_id}")
    print(f"Title: {title}")
    print(f"Status: {status}")
    print(f"Image URL: {image_url if image_url else 'NULL'}")
    
    if image_url:
        # Test if image is accessible
        try:
            response = requests.head(image_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Image accessible (HTTP {response.status_code})")
            else:
                print(f"❌ Image not accessible (HTTP {response.status_code})")
        except Exception as e:
            print(f"❌ Error accessing image: {str(e)[:100]}")
    else:
        print(f"⚠️  No image URL!")
    
    print()

cursor.close()
conn.close()

print("\n💡 If images are NULL, the events need to be re-synced")
print("💡 If images return 404, there's a Supabase storage issue")

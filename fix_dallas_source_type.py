"""
Update existing Dallas Arboretum events to use DALLAS_ARBORETUM (uppercase)
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

print("🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print("✅ Connected\n")

# Update source_type from lowercase to uppercase
print("🔧 Updating Dallas Arboretum source_type to uppercase...")

cursor.execute("""
    UPDATE events 
    SET source_type = 'DALLAS_ARBORETUM'
    WHERE source_type = 'dallas_arboretum'
    RETURNING id, title
""")

updated_events = cursor.fetchall()

print(f"✅ Updated {len(updated_events)} events\n")

for event in updated_events:
    event_id, title = event
    print(f"✅ {title[:60]}")

print("\n🎉 All events updated to DALLAS_ARBORETUM!")

cursor.close()
conn.close()

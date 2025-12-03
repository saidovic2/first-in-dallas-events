"""
Check what happened in the most recent Dallas Arboretum sync
"""
import psycopg2
from datetime import datetime, timedelta

DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

print("🔗 Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("✅ Connected\n")

# Check how many Dallas Arboretum events exist
print("📊 Total Dallas Arboretum Events in Database:")
cursor.execute("""
    SELECT COUNT(*) 
    FROM events 
    WHERE source_type = 'DALLAS_ARBORETUM'
""")
total = cursor.fetchone()[0]
print(f"   Total: {total} events\n")

# Check recent Dallas Arboretum events (last hour)
print("🕐 Events Added in Last Hour:")
cursor.execute("""
    SELECT id, title, created_at
    FROM events 
    WHERE source_type = 'DALLAS_ARBORETUM'
    AND created_at > NOW() - INTERVAL '1 hour'
    ORDER BY created_at DESC
""")
recent = cursor.fetchall()
print(f"   Recent: {len(recent)} events\n")
for event in recent:
    print(f"   - [{event[0]}] {event[1]}")
    print(f"     Created: {event[2]}")

# Check all Dallas Arboretum event titles to see if there are duplicates
print("\n📋 All Dallas Arboretum Event Titles:")
cursor.execute("""
    SELECT title, COUNT(*) as count
    FROM events 
    WHERE source_type = 'DALLAS_ARBORETUM'
    GROUP BY title
    ORDER BY count DESC, title
""")
titles = cursor.fetchall()
for title, count in titles:
    marker = "⚠️ " if count > 1 else "   "
    print(f"{marker}{title} ({count})")

# Check the most recent task
print("\n📋 Recent Sync Tasks:")
cursor.execute("""
    SELECT id, url, source_type, status, error_message, created_at
    FROM tasks
    WHERE source_type = 'dallas_arboretum_bulk'
    ORDER BY created_at DESC
    LIMIT 3
""")
tasks = cursor.fetchall()
for task in tasks:
    print(f"\n   Task {task[0]}:")
    print(f"   URL: {task[1]}")
    print(f"   Status: {task[3]}")
    print(f"   Created: {task[5]}")
    if task[4]:
        print(f"   Error: {task[4][:100]}")

cursor.close()
conn.close()

print("\n" + "="*60)
print("\n💡 Analysis:")
print("   - If total > recent: Events already existed (duplicates)")
print("   - If titles have count > 1: Duplicate event names")
print("   - Check task error_message for failures")

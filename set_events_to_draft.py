import requests

API_URL = "https://wonderful-vibrancy-production.up.railway.app/api"

# You'll need to login first to get a token
print("This script requires authentication.")
print("Please login to your CMS and:")
print("1. Open Browser DevTools (F12)")
print("2. Go to Application/Storage → Local Storage")
print("3. Find 'auth_token' value")
print("4. Paste it here:")
print()

token = input("Enter your auth token: ").strip()

if not token:
    print("❌ No token provided!")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Get all PUBLISHED events
print("\n🔍 Fetching PUBLISHED events...")
response = requests.get(f"{API_URL}/events?status=PUBLISHED&limit=500", headers=headers)

if response.status_code != 200:
    print(f"❌ Failed to fetch events: {response.status_code}")
    print(response.text)
    exit(1)

events = response.json()
print(f"✅ Found {len(events)} PUBLISHED events")

if len(events) == 0:
    print("✅ No PUBLISHED events to update!")
    exit(0)

# Ask for confirmation
print(f"\n⚠️  This will change {len(events)} events from PUBLISHED to DRAFT")
confirm = input("Continue? (yes/no): ").strip().lower()

if confirm != "yes":
    print("❌ Cancelled")
    exit(0)

# Update each event to DRAFT
print(f"\n📝 Updating events to DRAFT...")
updated_count = 0
failed_count = 0

for event in events:
    event_id = event['id']
    try:
        update_response = requests.patch(
            f"{API_URL}/events/{event_id}",
            headers=headers,
            json={"status": "DRAFT"}
        )
        
        if update_response.status_code == 200:
            updated_count += 1
            if updated_count % 10 == 0:
                print(f"  Updated {updated_count}/{len(events)}...")
        else:
            failed_count += 1
            print(f"  ❌ Failed to update event {event_id}: {update_response.status_code}")
    except Exception as e:
        failed_count += 1
        print(f"  ❌ Error updating event {event_id}: {e}")

print(f"\n✅ Done!")
print(f"  - Updated: {updated_count}")
print(f"  - Failed: {failed_count}")
print(f"\n🎉 All events are now DRAFT. Review them in your CMS and publish the ones you want!")

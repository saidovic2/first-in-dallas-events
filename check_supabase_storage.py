"""
Check Supabase Storage bucket configuration
"""
import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://jwlvikkbcjrnzsvhyfgy.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_KEY:
    print("❌ SUPABASE_SERVICE_ROLE_KEY not found in environment")
    exit(1)

print("🔗 Connecting to Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Connected to Supabase\n")

# Check if events bucket exists
print("📦 Checking storage buckets...")
try:
    buckets = supabase.storage.list_buckets()
    print(f"Found {len(buckets)} buckets:")
    
    events_bucket_found = False
    for bucket in buckets:
        is_public = "✅ PUBLIC" if bucket.get('public') else "🔒 PRIVATE"
        marker = "👉" if bucket['id'] == 'events' else "  "
        print(f"{marker} {bucket['id']}: {is_public}")
        if bucket['id'] == 'events':
            events_bucket_found = True
    
    if not events_bucket_found:
        print("\n❌ 'events' bucket NOT FOUND!")
        print("\n📝 Creating 'events' bucket...")
        supabase.storage.create_bucket('events', public=True)
        print("✅ Created 'events' bucket as PUBLIC")
    else:
        # Check if it's public
        for bucket in buckets:
            if bucket['id'] == 'events' and not bucket.get('public'):
                print("\n⚠️  'events' bucket exists but is PRIVATE!")
                print("Run the SQL fix: fix_supabase_storage.sql")
            elif bucket['id'] == 'events' and bucket.get('public'):
                print("\n✅ 'events' bucket is correctly configured as PUBLIC")
                
        # Test image access
        print("\n🖼️  Testing image access...")
        test_url = f"{SUPABASE_URL}/storage/v1/object/public/events/bulk-events/907277374a72.jpg"
        print(f"Sample URL: {test_url}")
        
        import requests
        response = requests.head(test_url, timeout=5)
        if response.status_code == 200:
            print("✅ Images are publicly accessible!")
        else:
            print(f"❌ Cannot access images (Status: {response.status_code})")
            print("   Run: fix_supabase_storage.sql in Supabase SQL Editor")

except Exception as e:
    print(f"❌ Error: {e}")

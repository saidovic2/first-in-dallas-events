"""
Direct test of Dallas Arboretum sync API endpoint
"""
import requests
import json

API_URL = "https://wonderful-vibrancy-production.up.railway.app"

print("🔍 Testing Dallas Arboretum API endpoint...\n")

# Test without auth first to see the error
print("1️⃣ Testing without authentication...")
try:
    response = requests.post(
        f"{API_URL}/api/sync/dallas-arboretum",
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Test health endpoint
print("2️⃣ Testing API health...")
try:
    response = requests.get(f"{API_URL}/health", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Check if docs are accessible
print("3️⃣ Testing API docs...")
try:
    response = requests.get(f"{API_URL}/docs", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ API is running and responding")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Try to get route list from OpenAPI
print("4️⃣ Checking available routes...")
try:
    response = requests.get(f"{API_URL}/openapi.json", timeout=10)
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get('paths', {})
        sync_routes = [path for path in paths.keys() if '/sync/' in path]
        print("   Available sync routes:")
        for route in sync_routes:
            print(f"      - {route}")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}\n")

print("=" * 60)
print("\n💡 Next Steps:")
print("   - If API is not responding: Check Railway API service logs")
print("   - If dallas-arboretum route is missing: API needs redeploy")
print("   - If getting 500 error: Check Redis/Database connection in API logs")

"""
Test Dallas Arboretum sync with authentication token
"""
import requests

API_URL = "https://wonderful-vibrancy-production.up.railway.app"

print("🔐 Testing Dallas Arboretum sync with authentication\n")

# Paste your token from browser's Local Storage
token = input("Paste your auth token from browser (DevTools > Application > Local Storage > token): ").strip()

if not token:
    print("❌ No token provided")
    exit(1)

print("\n🧪 Testing /api/sync/status endpoint...")
try:
    response = requests.get(
        f"{API_URL}/api/sync/status",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Authentication works!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🧪 Testing Dallas Arboretum sync endpoint...")
try:
    response = requests.post(
        f"{API_URL}/api/sync/dallas-arboretum",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Sync started successfully!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

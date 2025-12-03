"""
Test Dallas Arboretum sync API endpoint
"""
import requests
import os

# Get your API URL from environment or use default
API_URL = os.getenv("NEXT_PUBLIC_API_URL", "https://wonderful-vibrancy-production.up.railway.app")

print(f"🔗 Testing API at: {API_URL}")
print()

# You need to be authenticated - get token from browser
print("⚠️  You need an auth token from your browser:")
print("   1. Open CMS in browser")
print("   2. Open DevTools (F12)")
print("   3. Go to Application → Local Storage → token")
print("   4. Copy the token value")
print()

token = input("Paste your token here: ").strip()

if not token:
    print("❌ No token provided")
    exit(1)

print()
print("🧪 Testing Dallas Arboretum sync endpoint...")

try:
    response = requests.post(
        f"{API_URL}/api/sync/dallas-arboretum",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"Message: {data.get('message')}")
        print(f"Task ID: {data.get('task_id')}")
        print(f"Status: {data.get('status')}")
    else:
        print("❌ ERROR!")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out - API might be down")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - check if API is running")
except Exception as e:
    print(f"❌ Error: {e}")

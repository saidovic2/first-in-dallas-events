"""
Check if Facebook event URLs are still accessible
Flags events that have been deleted or made private
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import time

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("="*80)
print("🔍 CHECKING FACEBOOK EVENT URL HEALTH")
print("="*80)
print("\nThis will test if Facebook event URLs are still accessible.\n")

def check_url_health(url):
    """Check if URL is accessible"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Check status code
        if response.status_code == 200:
            return "✅ ACTIVE"
        elif response.status_code == 404:
            return "❌ DELETED"
        elif response.status_code == 403:
            return "🔒 PRIVATE/BLOCKED"
        else:
            return f"⚠️  STATUS {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⏱️  TIMEOUT"
    except requests.exceptions.RequestException as e:
        return "❌ ERROR"


def check_facebook_events(limit=20):
    """Check health of Facebook event URLs"""
    
    with engine.connect() as conn:
        # Get Facebook events
        result = conn.execute(text("""
            SELECT id, title, source_url, start_at
            FROM events 
            WHERE source_type = 'FACEBOOK'
            ORDER BY start_at DESC
            LIMIT :limit
        """), {"limit": limit})
        
        events = list(result)
        
        print(f"📋 Checking {len(events)} Facebook events...\n")
        
        active = 0
        deleted = 0
        blocked = 0
        errors = 0
        
        for i, event in enumerate(events, 1):
            print(f"[{i}/{len(events)}] {event.title[:40]}... ", end="")
            
            status = check_url_health(event.source_url)
            print(status)
            
            if "ACTIVE" in status:
                active += 1
            elif "DELETED" in status:
                deleted += 1
            elif "PRIVATE" in status or "BLOCKED" in status:
                blocked += 1
            else:
                errors += 1
            
            # Rate limiting - don't hammer Facebook
            time.sleep(0.5)
        
        print(f"\n{'='*80}")
        print(f"📊 URL HEALTH SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Active URLs: {active}")
        print(f"❌ Deleted: {deleted}")
        print(f"🔒 Private/Blocked: {blocked}")
        print(f"⚠️  Errors: {errors}")
        print(f"{'='*80}\n")
        
        if deleted > 0 or blocked > 0:
            print("⚠️  Some events are no longer accessible!")
            print("   Consider marking them as archived or updating their status.\n")


def main():
    limit = int(input("How many events to check? (default 20): ") or "20")
    print()
    check_facebook_events(limit)


if __name__ == "__main__":
    main()

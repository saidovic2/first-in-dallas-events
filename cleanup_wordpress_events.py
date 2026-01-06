"""
Cleanup WordPress Event Posts - Moves past events to trash
Deletes events that ended 24+ hours ago

Run this:
1. Manually: python cleanup_wordpress_events.py
2. Automatically: Before bulk sync
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from utils.wordpress import cleanup_past_wordpress_events
from config import settings

async def run_cleanup():
    """Run WordPress event cleanup"""
    
    print("🧹 WordPress Event Cleanup")
    print("=" * 50)
    print(f"WordPress: {settings.WP_BASE_URL}")
    print(f"Policy: Delete events 24+ hours after event date")
    print()
    
    # Confirm
    response = input("Continue with cleanup? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Cleanup cancelled")
        return
    
    print("\n🔍 Scanning WordPress for past events...")
    print()
    
    try:
        # Run cleanup
        result = await cleanup_past_wordpress_events(hours_after=24)
        
        print()
        print("=" * 50)
        print("📊 Cleanup Summary:")
        print(f"   Posts checked: {result['posts_checked']}")
        print(f"   Posts trashed: {result['trashed_count']}")
        print(f"   Cutoff time: {result['cutoff_time']}")
        print()
        
        if result['trashed_count'] > 0:
            print("✅ Cleanup complete!")
            print("💡 Trashed posts can be restored from WordPress admin within 30 days")
        else:
            print("✅ No past events found. WordPress is clean!")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_cleanup())

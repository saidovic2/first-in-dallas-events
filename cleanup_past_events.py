"""
Script to archive past events on WordPress (SEO-friendly)
Moves past events to 'Past Events' category instead of deleting
This preserves SEO value and prevents 404 errors
"""
import os
import sys
import asyncio

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from utils.wordpress import archive_past_wordpress_events

async def main():
    print("📦 Archiving Past Events (SEO-Friendly)")
    print("=" * 50)
    print("This will move past events to 'Past Events' category")
    print("instead of deleting them, preserving SEO value.\n")
    
    # Confirm action
    response = input("⚠️  Archive past events to 'Past Events' category? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Archive cancelled")
        return
    
    print("\n📊 Archiving WordPress posts...\n")
    
    try:
        result = await archive_past_wordpress_events(hours_after=24)
        
        print("\n" + "=" * 50)
        print("✅ Archive Complete!")
        print(f"   Posts checked: {result['posts_checked']}")
        print(f"   Posts archived: {result['archived_count']}")
        print(f"   Cutoff time: {result['cutoff_time']}")
        print("\n💡 Archived posts are now in 'Past Events' category")
        print("   URLs remain active for SEO purposes!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

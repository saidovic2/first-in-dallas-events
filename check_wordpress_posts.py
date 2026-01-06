"""
Check recent events and their WordPress post status
Shows which events have been published to WordPress
"""
import sys
import os
from datetime import datetime, timedelta, timezone

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from database import SessionLocal
from models.event import Event

def check_recent_posts():
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("📊 RECENT EVENTS & WORDPRESS POST STATUS")
        print("="*80)
        
        # Get events from last 7 days
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        recent_events = db.query(Event).filter(
            Event.created_at >= week_ago
        ).order_by(Event.created_at.desc()).limit(50).all()
        
        if not recent_events:
            print("\n❌ No events found in the last 7 days")
            return
        
        print(f"\n📅 Found {len(recent_events)} events from last 7 days\n")
        
        published_count = 0
        unpublished_count = 0
        
        print("STATUS | EVENT TITLE                                    | WP POST ID | WP URL")
        print("-" * 120)
        
        for event in recent_events:
            if event.wp_post_id:
                status = "✅ PUB "
                wp_url = f"https://firstindallas.com/?p={event.wp_post_id}"
                published_count += 1
            else:
                status = "⏳ PEND"
                wp_url = "Not published yet"
                unpublished_count += 1
            
            # Truncate title to 45 chars
            title = event.title[:45] + "..." if len(event.title) > 45 else event.title
            title = title.ljust(48)
            
            wp_id = str(event.wp_post_id) if event.wp_post_id else "N/A"
            
            print(f"{status} | {title} | {wp_id.ljust(10)} | {wp_url}")
        
        print("\n" + "="*80)
        print(f"📊 SUMMARY:")
        print(f"   ✅ Published to WordPress: {published_count}")
        print(f"   ⏳ Pending publication: {unpublished_count}")
        print("="*80)
        
        if unpublished_count > 0:
            print(f"\n💡 TIP: Unpublished events will be auto-published during next scheduled sync:")
            print(f"   - Next morning sync: 8:00 AM Central Time")
            print(f"   - Next evening sync: 6:00 PM Central Time")
            print(f"\n   Or manually publish now with:")
            print(f"   python sync_all_to_wordpress.py")
        
        if published_count > 0:
            print(f"\n🔗 Quick links to verify published posts:")
            for event in recent_events[:5]:  # Show first 5
                if event.wp_post_id:
                    print(f"   • {event.title[:50]}")
                    print(f"     https://firstindallas.com/?p={event.wp_post_id}")
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(check_recent_posts())

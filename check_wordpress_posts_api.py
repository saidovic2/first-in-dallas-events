"""
Check WordPress posts via WordPress REST API
Verifies which events have been published
"""
import os
import sys
import asyncio
import httpx
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

WP_BASE_URL = os.getenv("WP_BASE_URL", "https://firstindallas.com")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

async def check_wordpress_posts():
    """Check recent WordPress posts in Events category"""
    
    print("\n" + "="*80)
    print("📊 CHECKING WORDPRESS EVENTS POSTS")
    print("="*80)
    print(f"WordPress: {WP_BASE_URL}\n")
    
    if not all([WP_USER, WP_APP_PASSWORD]):
        print("❌ WordPress credentials not found in .env file")
        return 1
    
    auth = (WP_USER, WP_APP_PASSWORD)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get Events category ID
            cat_url = f"{WP_BASE_URL}/wp-json/wp/v2/categories?search=Events"
            cat_response = await client.get(cat_url, auth=auth)
            
            if cat_response.status_code != 200:
                print(f"❌ Failed to get Events category: {cat_response.status_code}")
                return 1
            
            categories = cat_response.json()
            events_cat_id = None
            
            for cat in categories:
                if cat['name'].lower() == 'events':
                    events_cat_id = cat['id']
                    break
            
            if not events_cat_id:
                print("❌ Events category not found")
                return 1
            
            print(f"✓ Found Events category (ID: {events_cat_id})\n")
            
            # Get recent posts from Events category
            posts_url = f"{WP_BASE_URL}/wp-json/wp/v2/posts"
            params = {
                "categories": events_cat_id,
                "per_page": 50,
                "orderby": "date",
                "order": "desc"
            }
            
            response = await client.get(posts_url, params=params, auth=auth)
            
            if response.status_code != 200:
                print(f"❌ Failed to get posts: {response.status_code}")
                return 1
            
            posts = response.json()
            
            if not posts:
                print("❌ No events posts found")
                return 1
            
            print(f"📋 Found {len(posts)} recent event posts\n")
            print("POST ID | DATE CREATED           | TITLE")
            print("-" * 100)
            
            for post in posts[:20]:  # Show first 20
                post_id = post['id']
                date_created = datetime.fromisoformat(post['date'].replace('Z', '+00:00'))
                date_str = date_created.strftime('%Y-%m-%d %I:%M %p')
                title = post['title']['rendered'][:70]
                
                print(f"{str(post_id).ljust(7)} | {date_str.ljust(22)} | {title}")
            
            if len(posts) > 20:
                print(f"\n... and {len(posts) - 20} more posts")
            
            print("\n" + "="*80)
            print("🔗 VERIFY YOUR POSTS:")
            print("="*80)
            
            # Show most recent 5 with full URLs
            for post in posts[:5]:
                post_id = post['id']
                title = post['title']['rendered'][:60]
                url = post['link']
                
                print(f"\n✅ {title}")
                print(f"   🔗 {url}")
                print(f"   📝 Post ID: {post_id}")
            
            print("\n" + "="*80)
            print(f"✅ TOTAL EVENT POSTS: {len(posts)}")
            print("="*80)
            print("\n💡 To check if specific events were published:")
            print("   - Compare event titles above with your recently added events")
            print("   - Click the URLs to view the posts on your site")
            print("   - Check for E-E-A-T content, breadcrumbs, and featured images\n")
            
    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(check_wordpress_posts())
    sys.exit(exit_code)

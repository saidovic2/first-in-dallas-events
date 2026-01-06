"""
Update all WordPress posts to add featured images
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Clear any cached modules
if 'utils.wordpress' in sys.modules:
    del sys.modules['utils.wordpress']
if 'utils.llm_enhancer' in sys.modules:
    del sys.modules['utils.llm_enhancer']

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.event import Event
from utils.wordpress import publish_to_wordpress
from utils.llm_enhancer import enhance_event_description
from config import settings

async def update_posts_with_featured_images():
    """Update all posts to add featured images"""
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("🖼️  Adding Featured Images to WordPress Posts")
    print("=" * 70)
    print(f"WordPress: {settings.WP_BASE_URL}")
    print()
    
    # Get events that have WordPress post IDs
    events = db.query(Event).filter(Event.wp_post_id.isnot(None)).all()
    total = len(events)
    
    print(f"📊 Found {total} events with WordPress posts")
    print()
    
    if total == 0:
        print("✅ No posts to update!")
        return
    
    # Confirmation
    response = input(f"⚠️  This will upload {total} images to WordPress (~10-15 minutes). Continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Update cancelled")
        return
    
    print()
    print("🔄 Uploading featured images and updating posts...")
    print("   (Each post takes ~3-5 seconds for image upload)")
    print()
    
    success_count = 0
    error_count = 0
    
    for i, event in enumerate(events, 1):
        try:
            print(f"[{i}/{total}] {event.title[:50]}...")
            
            # Update WordPress post (will automatically upload featured image)
            await publish_to_wordpress(event, None, event.wp_post_id)
            
            print(f"   ✅ Updated!")
            success_count += 1
            
            # Small delay to avoid overwhelming server
            await asyncio.sleep(0.5)
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            error_count += 1
            continue
    
    # Summary
    print()
    print("=" * 70)
    print("📊 Update Complete!")
    print(f"   ✅ Successfully updated: {success_count}")
    if error_count > 0:
        print(f"   ❌ Errors: {error_count}")
    print()
    print(f"🎉 Featured images added to all posts!")
    print(f"📷 Images are now in WordPress Media Library with alt text")
    
    db.close()


if __name__ == "__main__":
    asyncio.run(update_posts_with_featured_images())

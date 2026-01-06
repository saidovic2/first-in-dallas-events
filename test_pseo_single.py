"""
Test pSEO - Publish ONE event to WordPress using the new Gutenberg template
Run this to verify the template works before doing bulk sync
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from models.event import Event
from utils.wordpress import publish_to_wordpress
from utils.llm_enhancer import enhance_event_description
from config import settings

async def test_publish_single_event():
    """Test publishing a single event to WordPress with LLM enhancement"""
    
    # Connect to database
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Get the most recent PUBLISHED event
        event = db.query(Event)\
            .filter(Event.status == 'PUBLISHED')\
            .order_by(desc(Event.created_at))\
            .first()
        
        if not event:
            print("❌ No published events found in database")
            return
        
        print(f"📋 Testing with event: {event.title}")
        print(f"   Date: {event.start_at}")
        print(f"   Venue: {event.venue or 'N/A'}")
        print(f"   City: {event.city or 'N/A'}")
        print()
        
        # Check if WordPress credentials are configured
        if not all([settings.WP_BASE_URL, settings.WP_USER, settings.WP_APP_PASSWORD]):
            print("❌ WordPress credentials not configured!")
            print("\nPlease add to your .env file:")
            print("  WP_BASE_URL=https://your-wordpress-site.com")
            print("  WP_USER=your-wordpress-username")
            print("  WP_APP_PASSWORD=your-application-password")
            return
        
        print(f"🔗 WordPress URL: {settings.WP_BASE_URL}")
        print(f"👤 WordPress User: {settings.WP_USER}")
        print()
        
        # Check if LLM enhancement is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("🤖 LLM Enhancement: ENABLED (will generate unique description)")
        else:
            print("🤖 LLM Enhancement: DISABLED (add OPENAI_API_KEY to .env to enable)")
        print()
        
        # Generate LLM-enhanced description
        enhanced_description = None
        if openai_key:
            print("✍️  Generating enhanced description with AI...")
            event_data = {
                "title": event.title,
                "description": event.description,
                "venue": event.venue,
                "city": event.city,
                "category": event.category,
                "price_tier": event.price_tier
            }
            enhanced_description = await enhance_event_description(event_data, openai_key)
            print("✅ Enhanced description generated!")
            print()
        
        # Update or create WordPress post
        # Set to specific post ID to update existing post, or None to create new
        update_post_id = 3691  # Update this post instead of creating new ones
        
        if update_post_id:
            print(f"📤 Updating WordPress post {update_post_id}...")
        else:
            print("📤 Publishing new WordPress post...")
        
        post_id = await publish_to_wordpress(event, enhanced_description, update_post_id)
        
        print(f"✅ SUCCESS! Event {'updated' if update_post_id else 'published'} on WordPress")
        print(f"   WordPress Post ID: {post_id}")
        print(f"   View at: {settings.WP_BASE_URL}/wp-admin/post.php?post={post_id}&action=edit")
        print()
        
        if openai_key:
            print("🎉 The pSEO template with LLM enhancement is working!")
            print()
            print("Next steps:")
            print("1. Visit the WordPress post to see the AI-generated unique description")
            print("2. If satisfied, run bulk sync to publish all events with LLM enhancement")
        else:
            print("🎉 The pSEO template is working!")
            print()
            print("Next steps:")
            print("1. Add OPENAI_API_KEY to .env to enable AI-generated descriptions")
            print("2. Or run sync_all_to_wordpress.py to publish all events")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_publish_single_event())

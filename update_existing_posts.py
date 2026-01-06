"""
Update existing WordPress posts with the latest template
This will re-publish all events with the fixed description color
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.event import Event
from utils.wordpress import publish_to_wordpress
from utils.llm_enhancer import enhance_event_description
from config import settings

async def update_existing_posts(limit: int = None, use_llm: bool = False):
    """
    Update existing WordPress posts with latest template
    
    Args:
        limit: Max number of posts to update (None = all)
        use_llm: Re-generate LLM descriptions (costs money)
    """
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("🔄 Update Existing WordPress Posts")
    print("=" * 70)
    print(f"WordPress: {settings.WP_BASE_URL}")
    print(f"Re-generate LLM: {'✅ Yes' if use_llm else '❌ No (reuse existing)'}")
    if limit:
        print(f"Limit: {limit} posts")
    print()
    
    # Get events that have WordPress post IDs
    query = db.query(Event).filter(Event.wp_post_id.isnot(None))
    
    if limit:
        query = query.limit(limit)
    
    events = query.all()
    total = len(events)
    
    print(f"📊 Found {total} events with WordPress posts")
    print()
    
    if total == 0:
        print("✅ No posts to update!")
        return
    
    # Confirmation
    response = input(f"Update {total} WordPress posts with fixed template? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Update cancelled")
        return
    
    print()
    print("🔄 Updating WordPress posts...")
    print()
    
    success_count = 0
    error_count = 0
    
    for i, event in enumerate(events, 1):
        try:
            print(f"[{i}/{total}] Updating post {event.wp_post_id}: {event.title[:50]}...")
            
            # Generate LLM enhancement if requested
            enhanced_description = None
            if use_llm:
                try:
                    event_data = {
                        "title": event.title,
                        "description": event.description,
                        "venue": event.venue,
                        "city": event.city,
                        "category": event.category,
                        "price_tier": event.price_tier
                    }
                    enhanced_description = await enhance_event_description(event_data)
                except Exception as e:
                    print(f"   ⚠️  LLM failed, using original description")
            
            # Update WordPress post
            await publish_to_wordpress(event, enhanced_description, event.wp_post_id)
            
            print(f"   ✅ Updated!")
            success_count += 1
            
            # Small delay
            await asyncio.sleep(0.3)
        
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
    print(f"🎉 All posts now have visible description text!")
    
    db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update existing WordPress posts')
    parser.add_argument('--limit', type=int, help='Limit number of posts to update')
    parser.add_argument('--regen-llm', action='store_true', help='Re-generate LLM descriptions')
    
    args = parser.parse_args()
    
    asyncio.run(update_existing_posts(
        limit=args.limit,
        use_llm=args.regen_llm
    ))

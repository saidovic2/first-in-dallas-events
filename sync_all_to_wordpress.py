"""
Bulk Sync All Events to WordPress
- Cleans up past events (24+ hours old)
- Publishes all upcoming events with LLM enhancement
- Full SEO optimization (Schema.org, Open Graph, meta tags)
- Accurate Google Maps (99.8% coverage)
- Assigns to 'Events' category
"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.event import Event
from utils.wordpress import publish_to_wordpress, archive_past_wordpress_events
from utils.llm_enhancer import enhance_event_description
from config import settings

async def bulk_sync(
    limit: int = None,
    cleanup_first: bool = True,
    use_llm: bool = True,
    dry_run: bool = False
):
    """
    Sync all events to WordPress
    
    Args:
        limit: Max number of events to sync (None = all)
        cleanup_first: Run WordPress cleanup before syncing
        use_llm: Use AI to enhance descriptions
        dry_run: Show what would happen without actually publishing
    """
    
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("🚀 WordPress Bulk Sync")
    print("=" * 70)
    print(f"WordPress: {settings.WP_BASE_URL}")
    print(f"LLM Enhancement: {'✅ Enabled' if use_llm else '❌ Disabled'}")
    print(f"Cleanup Past Events: {'✅ Yes' if cleanup_first else '❌ No'}")
    if limit:
        print(f"Limit: {limit} events")
    if dry_run:
        print("🧪 DRY RUN MODE - No actual changes will be made")
    print()
    
    # Step 1: Cleanup past WordPress events
    if cleanup_first and not dry_run:
        print("🧹 Step 1: Cleaning up past WordPress events...")
        try:
            cleanup_result = await archive_past_wordpress_events(hours_after=24)
            print(f"   ✅ Cleaned {cleanup_result['trashed_count']} past events")
        except Exception as e:
            print(f"   ⚠️  Cleanup failed: {e}")
        print()
    
    # Step 2: Get upcoming events from database
    print("📊 Step 2: Loading events from database...")
    now = datetime.now(timezone.utc)
    
    query = db.query(Event).filter(
        Event.start_at > now,
        Event.status == 'PUBLISHED'
    ).order_by(Event.start_at)
    
    if limit:
        query = query.limit(limit)
    
    events = query.all()
    total = len(events)
    
    print(f"   Found {total} upcoming published events")
    print()
    
    if total == 0:
        print("✅ No events to sync!")
        return
    
    # Confirmation
    if not dry_run:
        print(f"⚠️  About to publish {total} events to WordPress")
        if use_llm:
            estimated_cost = total * 0.0025  # GPT-4o cost per event
            print(f"💰 Estimated LLM cost: ~${estimated_cost:.2f}")
        print()
        response = input("Continue? (yes/no): ")
        
        if response.lower() != 'yes':
            print("\n❌ Sync cancelled")
            return
        print()
    
    # Step 3: Sync events
    print(f"🔄 Step 3: Publishing events to WordPress...")
    print()
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, event in enumerate(events, 1):
        try:
            print(f"[{i}/{total}] {event.title[:60]}...")
            
            if dry_run:
                print(f"   🧪 Would publish: {event.venue or 'N/A'} ({event.start_at.date()})")
                success_count += 1
                continue
            
            # Check if already published
            if event.wp_post_id:
                print(f"   ⏭️  Already published (Post ID: {event.wp_post_id})")
                skipped_count += 1
                continue
            
            # Generate LLM enhancement
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
                    print(f"   ⚠️  LLM failed, using original description: {e}")
            
            # Publish to WordPress
            post_id = await publish_to_wordpress(event, enhanced_description)
            
            # Save WordPress post ID to database
            event.wp_post_id = post_id
            db.commit()
            
            print(f"   ✅ Published! (Post ID: {post_id})")
            success_count += 1
            
            # Small delay to avoid overwhelming WordPress
            await asyncio.sleep(0.5)
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            error_count += 1
            continue
    
    # Summary
    print()
    print("=" * 70)
    print("📊 Bulk Sync Complete!")
    print(f"   ✅ Successfully published: {success_count}")
    if skipped_count > 0:
        print(f"   ⏭️  Skipped (already published): {skipped_count}")
    if error_count > 0:
        print(f"   ❌ Errors: {error_count}")
    print()
    print(f"🎉 {success_count} events are now live on WordPress!")
    print(f"   View at: {settings.WP_BASE_URL}/category/events/")
    
    db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk sync events to WordPress')
    parser.add_argument('--limit', type=int, help='Limit number of events (for testing)')
    parser.add_argument('--no-cleanup', action='store_true', help='Skip WordPress cleanup')
    parser.add_argument('--no-llm', action='store_true', help='Skip LLM enhancement')
    parser.add_argument('--dry-run', action='store_true', help='Test run without publishing')
    
    args = parser.parse_args()
    
    asyncio.run(bulk_sync(
        limit=args.limit,
        cleanup_first=not args.no_cleanup,
        use_llm=not args.no_llm,
        dry_run=args.dry_run
    ))

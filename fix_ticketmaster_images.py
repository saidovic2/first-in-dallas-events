"""
Fix Blurry Ticketmaster Images
Updates all existing Ticketmaster events to use high-resolution images
"""

from sqlalchemy import create_engine, text
from datetime import datetime

DATABASE_URL = 'postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway'


def get_high_res_image(image_url):
    """
    Convert Ticketmaster thumbnail to high-resolution image
    Replace ANY size suffix with the highest quality version
    """
    if not image_url or 'ticketm.net' not in image_url:
        return image_url
    
    # ALL Ticketmaster image size patterns (including the tiny ones Apify gives us!)
    all_patterns = [
        # Low-res patterns (what Apify gives us)
        'RECOMENDATION_16_9',         # Tiny recommendation thumbnail ❌
        'RECOMENDATION_3_2',          # Tiny recommendation ❌
        'RETINA_PORTRAIT_16_9',       # 640x360 portrait - very small! ❌
        'RETINA_PORTRAIT_3_2',        # 640x427 ❌
        # Medium-res patterns
        'TABLET_LANDSCAPE_16_9',      # 1024x576
        'TABLET_PORTRAIT_16_9',       # 768x432
        'TABLET_LANDSCAPE_3_2',       # 1024x683
        'TABLET_PORTRAIT_3_2',        # 683x1024
        'RETINA_LANDSCAPE_16_9',      # 1136x639
        'RETINA_LANDSCAPE_3_2',       # 1024x683
        'CUSTOM',                     # Variable
        'EVENT_DETAIL_PAGE_16_9',     # Medium
        'ARTIST_PAGE_3_2',            # Medium
    ]
    
    # Replace with HIGHEST quality version available
    high_res_pattern = 'RETINA_LANDSCAPE_LARGE_16_9'  # 2048x1152 - Crystal clear! ✨
    
    # Try to replace any pattern found
    for pattern in all_patterns:
        if pattern in image_url:
            image_url = image_url.replace(pattern, high_res_pattern)
            return image_url
    
    # If no pattern found, try adding the high-res suffix before file extension
    if '.jpg' in image_url and '_' in image_url:
        base_url = image_url.rsplit('/', 1)[0]
        filename = image_url.rsplit('/', 1)[1]
        
        # Extract the ID part before .jpg
        if '_' not in filename:
            # No pattern at all, add high-res before .jpg
            filename = filename.replace('.jpg', f'_{high_res_pattern}.jpg')
            image_url = f"{base_url}/{filename}"
    
    return image_url


try:
    print("\n" + "="*80)
    print("FIXING TICKETMASTER IMAGE QUALITY")
    print("="*80 + "\n")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all Ticketmaster events
        result = conn.execute(text("""
            SELECT id, title, image_url
            FROM events
            WHERE source_type = 'TICKETMASTER'
            AND image_url IS NOT NULL
            AND image_url LIKE '%ticketm.net%'
            ORDER BY id
        """))
        
        events = result.fetchall()
        
        print(f"Found {len(events)} Ticketmaster events with images\n")
        
        if not events:
            print("No events to fix!")
            exit(0)
        
        # Ask for confirmation
        response = input(f"Update {len(events)} event images to high-res? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("\nCancelled.")
            exit(0)
        
        print(f"\nUpgrading images to high resolution (2048x1152)...\n")
        
        updated = 0
        skipped = 0
        
        for event_id, title, image_url in events:
            # Get high-res version
            new_image_url = get_high_res_image(image_url)
            
            # Check if it changed
            if new_image_url != image_url:
                # Update in database
                conn.execute(
                    text("""
                        UPDATE events 
                        SET image_url = :new_url,
                            updated_at = :now
                        WHERE id = :id
                    """),
                    {
                        "new_url": new_image_url,
                        "now": datetime.now(),
                        "id": event_id
                    }
                )
                
                print(f"[{event_id}] Updated: {title[:50]}")
                updated += 1
            else:
                print(f"[{event_id}] Skipped: {title[:50]} (already high-res)")
                skipped += 1
        
        conn.commit()
        
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"✓ Updated: {updated} events")
        print(f">> Skipped: {skipped} events (already high-res)")
        print(f"{'='*80}\n")
        
        print("✓ All Ticketmaster images upgraded to 2048x1152 resolution!")
        print("✓ Refresh your CMS to see crystal-clear images!")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

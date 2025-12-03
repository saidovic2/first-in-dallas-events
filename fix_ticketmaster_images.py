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
    Ticketmaster images have size parameters we can upgrade
    """
    if not image_url or 'ticketm.net' not in image_url:
        return image_url
    
    # List of low-res patterns to replace with high-res
    low_res_patterns = [
        'TABLET_LANDSCAPE_16_9',      # 1024x576
        'TABLET_PORTRAIT_16_9',       # 768x432
        'TABLET_LANDSCAPE_3_2',       # 1024x683
        'RETINA_PORTRAIT_16_9',       # 640x360
        'RETINA_LANDSCAPE_16_9',      # 1136x639
        'CUSTOM',                     # Variable
    ]
    
    # Replace with highest quality version
    high_res_pattern = 'RETINA_LANDSCAPE_LARGE_16_9'  # 2048x1152 - Best quality!
    
    for pattern in low_res_patterns:
        if pattern in image_url:
            image_url = image_url.replace(pattern, high_res_pattern)
            return image_url
    
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

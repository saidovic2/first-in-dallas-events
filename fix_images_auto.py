"""
Fix Blurry Ticketmaster Images - Auto-run version
"""

from sqlalchemy import create_engine, text
from datetime import datetime

DATABASE_URL = 'postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway'


def get_high_res_image(image_url):
    """Convert Ticketmaster thumbnail to high-resolution image"""
    if not image_url or 'ticketm.net' not in image_url:
        return image_url
    
    # ALL patterns including the tiny ones Apify gives us
    all_patterns = [
        'RECOMENDATION_16_9',         # Apify's tiny thumbnails!
        'RECOMENDATION_3_2',
        'RETINA_PORTRAIT_16_9',       # Apify's portrait thumbnails!
        'RETINA_PORTRAIT_3_2',
        'TABLET_LANDSCAPE_16_9',
        'TABLET_PORTRAIT_16_9',
        'TABLET_LANDSCAPE_3_2',
        'TABLET_PORTRAIT_3_2',
        'RETINA_LANDSCAPE_16_9',
        'RETINA_LANDSCAPE_3_2',
        'CUSTOM',
        'EVENT_DETAIL_PAGE_16_9',
        'ARTIST_PAGE_3_2',
    ]
    
    high_res_pattern = 'RETINA_LANDSCAPE_LARGE_16_9'  # 2048x1152!
    
    for pattern in all_patterns:
        if pattern in image_url:
            return image_url.replace(pattern, high_res_pattern)
    
    return image_url


try:
    print("\n" + "="*80)
    print("FIXING TICKETMASTER IMAGE QUALITY (AUTO-RUN)")
    print("="*80 + "\n")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
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
        print(f"Upgrading to high resolution (2048x1152)...\n")
        
        updated = 0
        skipped = 0
        
        for event_id, title, image_url in events:
            new_image_url = get_high_res_image(image_url)
            
            if new_image_url != image_url:
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
                
                if updated < 10 or updated % 100 == 0:
                    print(f"[{event_id}] Updated: {title[:50]}")
                updated += 1
            else:
                if skipped < 5:
                    print(f"[{event_id}] Already high-res: {title[:50]}")
                skipped += 1
        
        conn.commit()
        
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"✓ Updated: {updated} events → 2048x1152 resolution")
        print(f">> Skipped: {skipped} events (already high-res)")
        print(f"{'='*80}\n")
        
        if updated > 0:
            print("✓ All Ticketmaster images upgraded!")
            print("✓ Hard refresh your CMS (Ctrl+Shift+R) to see crystal-clear images!")
        else:
            print("✓ All images already at highest resolution!")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

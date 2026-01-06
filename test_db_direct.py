"""Direct database test without config dependencies"""
from sqlalchemy import create_engine, text
from datetime import datetime

# Railway database URL
DATABASE_URL = 'postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway'

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Test insert
        sql = text("""
            INSERT INTO events (
                title, source_url, venue, address, city,
                start_at, description, image_url,
                price_tier, category, source_type,
                fid_hash, status
            ) VALUES (
                :title, :url, :venue, :address, :city,
                :start_at, :description, :image_url,
                :price_tier, :category, :source_type,
                :fid_hash, :status
            ) RETURNING id
        """)
        
        result = conn.execute(sql, {
            'title': 'Test Ticketmaster Event',
            'url': 'https://www.ticketmaster.com/test?CAMEFROM=CMPAFFILIATE_6497023',
            'venue': 'American Airlines Center',
            'address': '2500 Victory Avenue, Dallas, TX',
            'city': 'Dallas',
            'start_at': datetime(2025, 12, 15, 19, 0),
            'description': 'Test event from Apify import',
            'image_url': 'https://s1.ticketm.net/dam/test.jpg',
            'price_tier': 'PAID',
            'category': 'Music & Concerts',
            'source_type': 'TICKETMASTER',
            'fid_hash': 'test123abc456def789',
            'status': 'DRAFT'
        })
        
        event_id = result.fetchone()[0]
        conn.commit()
        
        print(f"[OK] Successfully inserted event with ID: {event_id}")
        print(f"[OK] Database connection working!")
        
        # Check total events
        result = conn.execute(text("SELECT COUNT(*) FROM events WHERE source_type = 'TICKETMASTER'"))
        count = result.fetchone()[0]
        print(f"[INFO] Total Ticketmaster events in database: {count}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

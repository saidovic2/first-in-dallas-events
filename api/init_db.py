from database import engine, Base, SessionLocal
from models import User, Event, Source, Task
from utils.auth import get_password_hash
from datetime import datetime, timedelta
import hashlib

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

def seed_data():
    """Seed initial data"""
    db = SessionLocal()
    
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                name="Admin User",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin)
            print("✓ Admin user created (admin@example.com / admin123)")
        
        # Check if sample events exist
        event_count = db.query(Event).count()
        if event_count == 0:
            # Create sample events
            sample_events = [
                {
                    "title": "Summer Music Festival 2024",
                    "description": "Join us for an amazing outdoor music festival featuring local and international artists. Food trucks, craft beer, and great vibes!",
                    "start_at": datetime.now() + timedelta(days=15),
                    "end_at": datetime.now() + timedelta(days=17),
                    "venue": "Central Park Amphitheater",
                    "address": "123 Park Avenue",
                    "city": "New York",
                    "price_tier": "paid",
                    "price_amount": 75.00,
                    "image_url": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800",
                    "source_url": "https://example.com/summer-festival",
                    "source_type": "webpage",
                    "category": "Music",
                    "status": "published"
                },
                {
                    "title": "Tech Startup Networking Mixer",
                    "description": "Connect with fellow entrepreneurs, investors, and tech enthusiasts. Pitch your ideas and make valuable connections.",
                    "start_at": datetime.now() + timedelta(days=5),
                    "end_at": datetime.now() + timedelta(days=5, hours=3),
                    "venue": "Innovation Hub",
                    "address": "456 Tech Street",
                    "city": "San Francisco",
                    "price_tier": "free",
                    "image_url": "https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=800",
                    "source_url": "https://example.com/tech-mixer",
                    "source_type": "webpage",
                    "category": "Business",
                    "status": "published"
                },
                {
                    "title": "Community Yoga in the Park",
                    "description": "Free weekly yoga session for all levels. Bring your own mat and enjoy a peaceful morning practice.",
                    "start_at": datetime.now() + timedelta(days=2),
                    "end_at": datetime.now() + timedelta(days=2, hours=1),
                    "venue": "Riverside Park",
                    "address": "789 River Road",
                    "city": "Portland",
                    "price_tier": "free",
                    "image_url": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800",
                    "source_url": "https://example.com/yoga-park",
                    "source_type": "webpage",
                    "category": "Health & Wellness",
                    "status": "published"
                },
                {
                    "title": "Local Art Gallery Opening",
                    "description": "Celebrate the opening of our new contemporary art exhibition featuring works by emerging local artists.",
                    "start_at": datetime.now() + timedelta(days=8),
                    "end_at": datetime.now() + timedelta(days=8, hours=4),
                    "venue": "Downtown Art Gallery",
                    "address": "321 Art Boulevard",
                    "city": "Chicago",
                    "price_tier": "free",
                    "image_url": "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800",
                    "source_url": "https://example.com/art-opening",
                    "source_type": "webpage",
                    "category": "Arts & Culture",
                    "status": "published"
                },
                {
                    "title": "Food Truck Festival",
                    "description": "Over 50 food trucks serving cuisine from around the world. Live music, family activities, and great food!",
                    "start_at": datetime.now() + timedelta(days=20),
                    "end_at": datetime.now() + timedelta(days=20, hours=8),
                    "venue": "Waterfront Plaza",
                    "address": "555 Harbor Drive",
                    "city": "Seattle",
                    "price_tier": "free",
                    "image_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800",
                    "source_url": "https://example.com/food-festival",
                    "source_type": "webpage",
                    "category": "Food & Drink",
                    "status": "published"
                },
                {
                    "title": "Charity Run for Education",
                    "description": "5K and 10K run to support local schools. All proceeds go to education programs.",
                    "start_at": datetime.now() + timedelta(days=12),
                    "end_at": datetime.now() + timedelta(days=12, hours=3),
                    "venue": "City Stadium",
                    "address": "888 Sports Way",
                    "city": "Boston",
                    "price_tier": "paid",
                    "price_amount": 25.00,
                    "image_url": "https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=800",
                    "source_url": "https://example.com/charity-run",
                    "source_type": "webpage",
                    "category": "Sports",
                    "status": "draft"
                }
            ]
            
            for event_data in sample_events:
                # Generate unique hash
                hash_string = f"{event_data['title']}{event_data['start_at']}{event_data['source_url']}"
                fid_hash = hashlib.md5(hash_string.encode()).hexdigest()
                event_data['fid_hash'] = fid_hash
                
                event = Event(**event_data)
                db.add(event)
            
            print(f"✓ Created {len(sample_events)} sample events")
        
        # Create sample tasks
        task_count = db.query(Task).count()
        if task_count == 0:
            sample_tasks = [
                {
                    "url": "https://example.com/event1",
                    "source_type": "webpage",
                    "status": "done",
                    "logs": "Successfully extracted 1 event",
                    "events_extracted": 1
                },
                {
                    "url": "https://example.com/event2",
                    "source_type": "facebook",
                    "status": "done",
                    "logs": "Successfully extracted 1 event",
                    "events_extracted": 1
                },
                {
                    "url": "https://example.com/invalid",
                    "source_type": "webpage",
                    "status": "failed",
                    "error_message": "No event data found on page",
                    "events_extracted": 0
                }
            ]
            
            for task_data in sample_tasks:
                task = Task(**task_data)
                db.add(task)
            
            print(f"✓ Created {len(sample_tasks)} sample tasks")
        
        db.commit()
        print("✓ Database seeded successfully")
        
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    create_tables()
    seed_data()
    print("Database initialization complete!")

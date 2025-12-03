"""
Add dallas_arboretum to sourcetype enum
"""
import os
import sys
from sqlalchemy import create_engine, text

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/events_cms")

print(f"🔗 Connecting to database...")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("✅ Connected to database")
        
        # Add the new enum value
        print("📝 Adding 'dallas_arboretum' to sourcetype enum...")
        
        # PostgreSQL doesn't support IF NOT EXISTS for ALTER TYPE in older versions
        # So we'll try to add it and catch the error if it already exists
        try:
            conn.execute(text("ALTER TYPE sourcetype ADD VALUE 'dallas_arboretum'"))
            conn.commit()
            print("✅ Successfully added 'dallas_arboretum' to sourcetype enum")
        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️  'dallas_arboretum' already exists in sourcetype enum")
            else:
                raise e
        
        # Verify the change
        print("\n📋 Current sourcetype enum values:")
        result = conn.execute(text("SELECT unnest(enum_range(NULL::sourcetype))::text"))
        for row in result:
            print(f"   - {row[0]}")
        
        print("\n✅ Migration completed successfully!")
        print("\n🎉 You can now run the Dallas Arboretum sync!")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

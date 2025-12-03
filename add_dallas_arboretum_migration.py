"""
Add dallas_arboretum to sourcetype enum
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    exit(1)

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

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

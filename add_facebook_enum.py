"""Add FACEBOOK to source_type enum in Railway database"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("🔧 Adding FACEBOOK to source_type enum...")

try:
    with engine.connect() as conn:
        # Add FACEBOOK to the enum
        conn.execute(text("""
            ALTER TYPE source_type ADD VALUE IF NOT EXISTS 'FACEBOOK';
        """))
        conn.commit()
        print("✅ FACEBOOK enum value added successfully!")
        
        # Verify
        result = conn.execute(text("""
            SELECT enum_range(NULL::source_type);
        """))
        enums = result.scalar()
        print(f"📋 Current source_type values: {enums}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nNote: If FACEBOOK already exists, this is expected.")

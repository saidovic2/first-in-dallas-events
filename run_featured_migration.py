#!/usr/bin/env python3
"""
Run Featured Events System Migration
This script will add the featured events tables and columns to your database.
"""

import sys
sys.path.append('./api')

from sqlalchemy import create_engine, text
from config import settings

def run_migration():
    """Execute the featured events migration"""
    
    print("🚀 Running Featured Events Migration...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    print()
    
    engine = create_engine(settings.DATABASE_URL)
    
    with open('add_featured_events_system.sql', 'r') as f:
        sql = f.read()
    
    try:
        with engine.connect() as conn:
            # Execute migration
            conn.execute(text(sql))
            conn.commit()
            
            print("✅ Migration completed successfully!")
            print()
            print("📋 Created:")
            print("  - featured_slots table")
            print("  - featured_pricing table")
            print("  - Added is_featured, featured_tier, featured_until columns to events")
            print("  - Created indexes for performance")
            print("  - Inserted default pricing tiers")
            print()
            
            # Show pricing tiers
            result = conn.execute(text("SELECT tier, slot_position, base_price_weekly FROM featured_pricing ORDER BY slot_position"))
            
            print("💰 Pricing Tiers:")
            for row in result:
                print(f"  {row.tier:10} (Position {row.slot_position}): ${row.base_price_weekly}/week")
            
            print()
            print("🎯 Next Steps:")
            print("  1. Restart your API server")
            print("  2. Check API docs at /docs for new /api/featured endpoints")
            print("  3. Update WordPress plugin with featured section")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print()
        print("💡 Troubleshooting:")
        print("  - Make sure your database is running")
        print("  - Check DATABASE_URL in .env file")
        print("  - Verify you have CREATE TABLE permissions")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()

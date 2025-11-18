#!/usr/bin/env python3
"""
Featured Events Migration Script
Run with: railway run --service wonderful-vibrancy python migrate_featured.py
"""
import psycopg2
import os
import sys

def main():
    print("\n🚀 Featured Events Migration\n")
    print("=" * 60)
    
    try:
        # Connect using DATABASE_URL
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found")
            sys.exit(1)
        
        # Replace internal hostname with public one if needed
        if 'postgres.railway.internal' in database_url:
            # Get public connection details
            host = os.environ.get('PGHOST', 'shortline.proxy.rlwy.net')
            port = os.environ.get('PGPORT', '49460')
            database = os.environ.get('PGDATABASE', 'railway')
            user = os.environ.get('PGUSER', 'postgres')
            password = os.environ.get('PGPASSWORD')
            
            database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        print(f"📡 Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()
        print("✅ Connected!\n")
        
        # Migration steps
        migrations = [
            ("Adding is_featured column", 
             "ALTER TABLE events ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE"),
            
            ("Adding featured_tier column",
             "ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_tier VARCHAR(20)"),
            
            ("Adding featured_until column",
             "ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_until TIMESTAMP WITH TIME ZONE"),
            
            ("Creating performance index",
             "CREATE INDEX IF NOT EXISTS idx_events_featured ON events(is_featured, featured_until) WHERE is_featured = TRUE"),
            
            ("Inserting pricing tiers",
             """INSERT INTO featured_pricing (tier, slot_position, base_price_weekly, discount_monthly, discount_quarterly, discount_yearly, description, features) 
             VALUES 
             ('PLATINUM', 1, 149.00, 10, 20, 35, 'Top-left position - Maximum visibility', '{"position": "Top-Left", "size": "Extra Large", "highlights": ["Badge", "Bold border", "Priority listing"]}'::jsonb),
             ('GOLD', 2, 99.00, 10, 20, 35, 'Top-right position - High visibility', '{"position": "Top-Right", "size": "Large", "highlights": ["Badge", "Bold text"]}'::jsonb),
             ('SILVER', 3, 69.00, 10, 20, 35, 'Bottom-left position - Good visibility', '{"position": "Bottom-Left", "size": "Medium", "highlights": ["Badge"]}'::jsonb),
             ('BRONZE', 4, 49.00, 10, 20, 35, 'Bottom-right position - Standard visibility', '{"position": "Bottom-Right", "size": "Medium", "highlights": ["Featured tag"]}'::jsonb)
             ON CONFLICT (tier) DO NOTHING"""),
        ]
        
        for i, (description, sql) in enumerate(migrations, 1):
            print(f"{i}. {description}...")
            try:
                cur.execute(sql)
                print(f"   ✅ Success")
            except Exception as e:
                print(f"   ⚠️  {str(e)[:100]}")
        
        # Verify
        print("\n📊 Verifying installation...")
        cur.execute("SELECT COUNT(*) FROM featured_pricing")
        count = cur.fetchone()[0]
        print(f"   💰 Pricing tiers: {count}")
        
        cur.execute("SELECT tier, slot_position, base_price_weekly FROM featured_pricing ORDER BY slot_position")
        tiers = cur.fetchall()
        for tier, pos, price in tiers:
            print(f"      - {tier:8} (Position {pos}): ${price}/week")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. API will restart automatically")
        print("2. Test: https://wonderful-vibrancy-production.up.railway.app/api/featured/pricing")
        print("3. Reactivate WordPress plugin")
        print()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

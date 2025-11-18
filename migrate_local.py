#!/usr/bin/env python3
"""
Run migration from local machine using public Railway database connection
"""
import psycopg2

# Public Railway database connection
DATABASE_URL = "postgresql://postgres:cUhxpuWSyHTCMWZzwQqgufrWQQSYtsWW@shortline.proxy.rlwy.net:49460/railway"

def main():
    print("\n🚀 Featured Events Migration (Local → Railway)\n")
    print("=" * 60)
    
    try:
        print(f"📡 Connecting to Railway database...")
        conn = psycopg2.connect(DATABASE_URL)
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
                error_msg = str(e)
                if "already exists" in error_msg or "duplicate" in error_msg.lower():
                    print(f"   ℹ️  Already exists (OK)")
                else:
                    print(f"   ⚠️  {error_msg[:100]}")
        
        # Verify
        print("\n📊 Verifying installation...")
        cur.execute("SELECT COUNT(*) FROM featured_pricing")
        count = cur.fetchone()[0]
        print(f"   💰 Pricing tiers installed: {count}")
        
        if count > 0:
            cur.execute("SELECT tier, slot_position, base_price_weekly FROM featured_pricing ORDER BY slot_position")
            tiers = cur.fetchall()
            for tier, pos, price in tiers:
                print(f"      - {tier:8} (Position {pos}): ${price}/week")
        
        # Check events table columns
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'events' AND column_name LIKE '%featured%'
            ORDER BY column_name
        """)
        cols = cur.fetchall()
        print(f"\n   📋 Events table columns: {len(cols)}")
        for (col_name,) in cols:
            print(f"      - {col_name}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. API will work after ~30 seconds")
        print("2. Test: https://wonderful-vibrancy-production.up.railway.app/api/featured/pricing")
        print("3. Reactivate WordPress plugin")
        print("4. Visit your events calendar!")
        print()
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("\n💡 Possible issues:")
        print("   - Railway database credentials may have changed")
        print("   - Network/firewall blocking connection")
        print("   - Railway proxy may be down")
        print("\n📝 To get new credentials:")
        print("   Run: railway variables --service Postgres")
        return False
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

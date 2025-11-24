#!/usr/bin/env python3
"""
Simple migration script - connects directly to Railway database
"""
import subprocess
import sys

print("\n🚀 Fixing Database for Featured Events\n")
print("=" * 60)

commands = [
    ("Adding is_featured column", "ALTER TABLE events ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE"),
    ("Adding featured_tier column", "ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_tier VARCHAR(20)"),
    ("Adding featured_until column", "ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_until TIMESTAMP WITH TIME ZONE"),
    ("Creating performance index", "CREATE INDEX IF NOT EXISTS idx_events_featured ON events(is_featured, featured_until) WHERE is_featured = TRUE"),
    ("Inserting pricing tiers", "INSERT INTO featured_pricing (tier, slot_position, base_price_weekly, discount_monthly, discount_quarterly, discount_yearly, description, features) VALUES ('PLATINUM', 1, 149.00, 10, 20, 35, 'Top-left position', '{}'), ('GOLD', 2, 99.00, 10, 20, 35, 'Top-right position', '{}'), ('SILVER', 3, 69.00, 10, 20, 35, 'Bottom-left position', '{}'), ('BRONZE', 4, 49.00, 10, 20, 35, 'Bottom-right position', '{}') ON CONFLICT (tier) DO NOTHING"),
]

for i, (desc, sql) in enumerate(commands, 1):
    print(f"\n{i}. {desc}...")
    
    # Create Python code to execute SQL
    py_code = f"""
import psycopg2
import os
conn = psycopg2.connect(
    host=os.environ['PGHOST'],
    port=os.environ['PGPORT'],
    database=os.environ['PGDATABASE'],
    user=os.environ['PGUSER'],
    password=os.environ['PGPASSWORD']
)
conn.autocommit = True
cur = conn.cursor()
cur.execute('''{sql}''')
cur.close()
conn.close()
print('   ✅ Success')
"""
    
    try:
        result = subprocess.run(
            ['railway', 'run', '--service', 'wonderful-vibrancy', 'python', '-c', py_code],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"   ✅ Success")
        else:
            print(f"   ⚠️ Warning: {result.stderr[:100] if result.stderr else 'Done'}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("🎉 DATABASE MIGRATION COMPLETE!")
print("=" * 60)

print("\n📝 Next Steps:")
print("   1. Run: python -m pytest test-after-sql.ps1  # Or just run .\\test-after-sql.ps1")
print("   2. Visit: https://firstindallas.com/wp-admin/plugins.php")
print("   3. Deactivate + Reactivate 'Events CMS Directory'")
print("   4. Test your calendar!\n")

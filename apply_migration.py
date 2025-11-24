#!/usr/bin/env python3
"""
Apply Featured Events migration to Railway database
"""
import subprocess
import sys

print("\n🚀 Applying Featured Events Migration to Railway Database\n")
print("=" * 60)

# Read the SQL file
print("\n📄 Reading SQL file...")
with open('RAILWAY_RUN_THIS.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

print("✅ SQL file loaded\n")

# Create a temporary script to execute via railway run
temp_sql = """
-- Step 1: Add featured columns to events table
ALTER TABLE events ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;
ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_tier VARCHAR(20);
ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_until TIMESTAMP WITH TIME ZONE;

-- Step 2: Create index
CREATE INDEX IF NOT EXISTS idx_events_featured ON events(is_featured, featured_until) WHERE is_featured = TRUE;

-- Step 3: Insert pricing tiers
INSERT INTO featured_pricing (tier, slot_position, base_price_weekly, discount_monthly, discount_quarterly, discount_yearly, description, features) VALUES
('PLATINUM', 1, 149.00, 10, 20, 35, 'Top-left position - Maximum visibility', '{"position": "Top-Left", "size": "Extra Large", "highlights": ["Badge", "Bold border", "Priority listing"]}'::jsonb),
('GOLD', 2, 99.00, 10, 20, 35, 'Top-right position - High visibility', '{"position": "Top-Right", "size": "Large", "highlights": ["Badge", "Bold text"]}'::jsonb),
('SILVER', 3, 69.00, 10, 20, 35, 'Bottom-left position - Good visibility', '{"position": "Bottom-Left", "size": "Medium", "highlights": ["Badge"]}'::jsonb),
('BRONZE', 4, 49.00, 10, 20, 35, 'Bottom-right position - Standard visibility', '{"position": "Bottom-Right", "size": "Medium", "highlights": ["Featured tag"]}'::jsonb)
ON CONFLICT (tier) DO NOTHING;
"""

# Save to a temporary file
with open('_temp_migration.sql', 'w', encoding='utf-8') as f:
    f.write(temp_sql)

print("📋 Migration steps:")
print("   1. Add featured columns to events table")
print("   2. Create performance index")
print("   3. Insert pricing tiers (Platinum, Gold, Silver, Bronze)")
print("\n⏳ Executing via Railway CLI...\n")

try:
    # Execute via railway run with python
    result = subprocess.run(
        ['railway', 'run', 'python', '-c', f'''
import psycopg2
import os

# Connect to database
conn = psycopg2.connect(
    host=os.environ.get("PGHOST"),
    port=os.environ.get("PGPORT"),
    database=os.environ.get("PGDATABASE"),
    user=os.environ.get("PGUSER"),
    password=os.environ.get("PGPASSWORD")
)
conn.autocommit = True
cur = conn.cursor()

sql = """{temp_sql}"""

# Execute
cur.execute(sql)

# Verify
cur.execute("SELECT tier, slot_position, base_price_weekly FROM featured_pricing ORDER BY slot_position")
rows = cur.fetchall()

print("\\n✅ Migration successful!")
print(f"\\n💰 Pricing tiers installed: {{len(rows)}}")
for row in rows:
    print(f"  - {{row[0]:8}} (Position {{row[1]}}): ${{row[2]}}/week")

cur.close()
conn.close()
'''],
        capture_output=True,
        text=True,
        cwd='.'
    )
    
    print(result.stdout)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("   1. Run: .\\test-after-sql.ps1")
        print("   2. Reactivate WordPress plugin")
        print("   3. Test your events calendar!\n")
    else:
        print(f"\n❌ Error: {result.stderr}")
        sys.exit(1)
        
except FileNotFoundError:
    print("\n❌ Error: psycopg2 not installed")
    print("\nInstall it with: pip install psycopg2-binary")
    print("Then run this script again")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {str(e)}")
    sys.exit(1)

# ============================================
# Run these commands ONE AT A TIME
# ============================================

Write-Host "`n🚀 Featured Events Migration - Step by Step`n" -ForegroundColor Cyan

# Command 1
Write-Host "📋 Command 1: Add is_featured column" -ForegroundColor Yellow
railway run --service wonderful-vibrancy -- python -c "import psycopg2, os; conn=psycopg2.connect(host=os.environ['PGHOST'], port=os.environ['PGPORT'], database=os.environ['PGDATABASE'], user=os.environ['PGUSER'], password=os.environ['PGPASSWORD']); conn.autocommit=True; cur=conn.cursor(); cur.execute('ALTER TABLE events ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE'); print('✅ Added is_featured column'); cur.close(); conn.close()"

# Command 2
Write-Host "`n📋 Command 2: Add featured_tier column" -ForegroundColor Yellow
railway run --service wonderful-vibrancy -- python -c "import psycopg2, os; conn=psycopg2.connect(host=os.environ['PGHOST'], port=os.environ['PGPORT'], database=os.environ['PGDATABASE'], user=os.environ['PGUSER'], password=os.environ['PGPASSWORD']); conn.autocommit=True; cur=conn.cursor(); cur.execute('ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_tier VARCHAR(20)'); print('✅ Added featured_tier column'); cur.close(); conn.close()"

# Command 3
Write-Host "`n📋 Command 3: Add featured_until column" -ForegroundColor Yellow
railway run --service wonderful-vibrancy -- python -c "import psycopg2, os; conn=psycopg2.connect(host=os.environ['PGHOST'], port=os.environ['PGPORT'], database=os.environ['PGDATABASE'], user=os.environ['PGUSER'], password=os.environ['PGPASSWORD']); conn.autocommit=True; cur=conn.cursor(); cur.execute('ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_until TIMESTAMP WITH TIME ZONE'); print('✅ Added featured_until column'); cur.close(); conn.close()"

# Command 4
Write-Host "`n📋 Command 4: Create index" -ForegroundColor Yellow
railway run --service wonderful-vibrancy -- python -c "import psycopg2, os; conn=psycopg2.connect(host=os.environ['PGHOST'], port=os.environ['PGPORT'], database=os.environ['PGDATABASE'], user=os.environ['PGUSER'], password=os.environ['PGPASSWORD']); conn.autocommit=True; cur=conn.cursor(); cur.execute('CREATE INDEX IF NOT EXISTS idx_events_featured ON events(is_featured, featured_until) WHERE is_featured = TRUE'); print('✅ Created index'); cur.close(); conn.close()"

# Command 5
Write-Host "`n📋 Command 5: Insert pricing tiers" -ForegroundColor Yellow
railway run --service wonderful-vibrancy -- python -c "import psycopg2, os; conn=psycopg2.connect(host=os.environ['PGHOST'], port=os.environ['PGPORT'], database=os.environ['PGDATABASE'], user=os.environ['PGUSER'], password=os.environ['PGPASSWORD']); conn.autocommit=True; cur=conn.cursor(); cur.execute(\"INSERT INTO featured_pricing (tier, slot_position, base_price_weekly, discount_monthly, discount_quarterly, discount_yearly, description, features) VALUES ('PLATINUM', 1, 149.00, 10, 20, 35, 'Top-left position', '{}'), ('GOLD', 2, 99.00, 10, 20, 35, 'Top-right position', '{}'), ('SILVER', 3, 69.00, 10, 20, 35, 'Bottom-left position', '{}'), ('BRONZE', 4, 49.00, 10, 20, 35, 'Bottom-right position', '{}') ON CONFLICT (tier) DO NOTHING\"); print('✅ Inserted pricing tiers'); cur.close(); conn.close()"

Write-Host "`n🎉 Migration Complete!" -ForegroundColor Green
Write-Host "`nNext: Run .\test-after-sql.ps1 to verify" -ForegroundColor Cyan

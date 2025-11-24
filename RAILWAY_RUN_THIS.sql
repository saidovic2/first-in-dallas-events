-- ========================================
-- RAILWAY: Run this SQL to complete setup
-- ========================================

-- Step 1: Add featured columns to events table
ALTER TABLE events ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;
ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_tier VARCHAR(20);
ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_until TIMESTAMP WITH TIME ZONE;

-- Step 2: Create index for performance
CREATE INDEX IF NOT EXISTS idx_events_featured ON events(is_featured, featured_until) WHERE is_featured = TRUE;

-- Step 3: Insert pricing tiers
INSERT INTO featured_pricing (tier, slot_position, base_price_weekly, discount_monthly, discount_quarterly, discount_yearly, description, features) VALUES
('PLATINUM', 1, 149.00, 10, 20, 35, 'Top-left position - Maximum visibility', 
 '{"position": "Top-Left", "size": "Extra Large", "highlights": ["Badge", "Bold border", "Priority listing"]}'::jsonb),
('GOLD', 2, 99.00, 10, 20, 35, 'Top-right position - High visibility',
 '{"position": "Top-Right", "size": "Large", "highlights": ["Badge", "Bold text"]}'::jsonb),
('SILVER', 3, 69.00, 10, 20, 35, 'Bottom-left position - Good visibility',
 '{"position": "Bottom-Left", "size": "Medium", "highlights": ["Badge"]}'::jsonb),
('BRONZE', 4, 49.00, 10, 20, 35, 'Bottom-right position - Standard visibility',
 '{"position": "Bottom-Right", "size": "Medium", "highlights": ["Featured tag"]}'::jsonb)
ON CONFLICT (tier) DO NOTHING;

-- Step 4: Verify everything
SELECT 'Events table columns:' as check_type;
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'events' AND column_name LIKE '%featured%';

SELECT 'Pricing tiers:' as check_type;
SELECT tier, slot_position, base_price_weekly FROM featured_pricing ORDER BY slot_position;

SELECT '✅ Setup complete!' as status;

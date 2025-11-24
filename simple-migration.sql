ALTER TABLE events ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;
ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_tier VARCHAR(20);
ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_until TIMESTAMP WITH TIME ZONE;
CREATE INDEX IF NOT EXISTS idx_events_featured ON events(is_featured, featured_until) WHERE is_featured = TRUE;
INSERT INTO featured_pricing (tier, slot_position, base_price_weekly, discount_monthly, discount_quarterly, discount_yearly, description, features) VALUES ('PLATINUM', 1, 149.00, 10, 20, 35, 'Top-left position - Maximum visibility', '{"position": "Top-Left"}'::jsonb), ('GOLD', 2, 99.00, 10, 20, 35, 'Top-right position - High visibility', '{"position": "Top-Right"}'::jsonb), ('SILVER', 3, 69.00, 10, 20, 35, 'Bottom-left position - Good visibility', '{"position": "Bottom-Left"}'::jsonb), ('BRONZE', 4, 49.00, 10, 20, 35, 'Bottom-right position - Standard visibility', '{"position": "Bottom-Right"}'::jsonb) ON CONFLICT (tier) DO NOTHING;
SELECT 'Migration complete - ' || COUNT(*) || ' pricing tiers' as status FROM featured_pricing;

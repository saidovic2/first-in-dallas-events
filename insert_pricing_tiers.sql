-- Insert default pricing tiers if they don't exist yet
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

-- Verify insertion
SELECT tier, slot_position, base_price_weekly, description FROM featured_pricing ORDER BY slot_position;

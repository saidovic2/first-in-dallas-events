-- ====================================
-- Featured Events Monetization System
-- Date: 2025-11-17
-- ====================================

-- 1. Create featured_slots table
CREATE TABLE IF NOT EXISTS featured_slots (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    
    -- Slot configuration
    slot_position INTEGER NOT NULL CHECK (slot_position BETWEEN 1 AND 4),
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('PLATINUM', 'GOLD', 'SILVER', 'BRONZE')),
    
    -- Pricing info
    price_paid DECIMAL(10, 2) NOT NULL,
    payment_frequency VARCHAR(20) NOT NULL DEFAULT 'WEEKLY',
    
    -- Timing
    starts_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ends_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Payment tracking
    payment_status VARCHAR(20) DEFAULT 'PAID' CHECK (payment_status IN ('PENDING', 'PAID', 'FAILED', 'REFUNDED', 'EXPIRED')),
    payment_method VARCHAR(50) DEFAULT 'MANUAL',
    notes TEXT,
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Add featured columns to events table
ALTER TABLE events ADD COLUMN IF NOT EXISTS is_featured BOOLEAN DEFAULT FALSE;
ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_tier VARCHAR(20);
ALTER TABLE events ADD COLUMN IF NOT EXISTS featured_until TIMESTAMP WITH TIME ZONE;

-- 3. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_featured_slots_active ON featured_slots(is_active, starts_at, ends_at) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_featured_slots_position ON featured_slots(slot_position, starts_at);
CREATE INDEX IF NOT EXISTS idx_events_featured ON events(is_featured, featured_until) WHERE is_featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_featured_slots_event ON featured_slots(event_id);

-- 4. Create pricing reference table
CREATE TABLE IF NOT EXISTS featured_pricing (
    id SERIAL PRIMARY KEY,
    tier VARCHAR(20) NOT NULL UNIQUE,
    slot_position INTEGER NOT NULL UNIQUE CHECK (slot_position BETWEEN 1 AND 4),
    base_price_weekly DECIMAL(10, 2) NOT NULL,
    discount_monthly INTEGER DEFAULT 10,
    discount_quarterly INTEGER DEFAULT 20,
    discount_yearly INTEGER DEFAULT 35,
    description TEXT,
    features JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Insert default pricing tiers
INSERT INTO featured_pricing (tier, slot_position, base_price_weekly, description, features) VALUES
('PLATINUM', 1, 149.00, 'Top-left position - Maximum visibility', 
 '{"position": "Top-Left", "size": "Extra Large", "highlights": ["Badge", "Bold border", "Priority listing"]}'::jsonb),
('GOLD', 2, 99.00, 'Top-right position - High visibility',
 '{"position": "Top-Right", "size": "Large", "highlights": ["Badge", "Bold text"]}'::jsonb),
('SILVER', 3, 69.00, 'Bottom-left position - Good visibility',
 '{"position": "Bottom-Left", "size": "Medium", "highlights": ["Badge"]}'::jsonb),
('BRONZE', 4, 49.00, 'Bottom-right position - Standard visibility',
 '{"position": "Bottom-Right", "size": "Medium", "highlights": ["Featured tag"]}'::jsonb)
ON CONFLICT (tier) DO NOTHING;

-- 6. Create helper function to get active featured events
CREATE OR REPLACE FUNCTION get_active_featured_events()
RETURNS TABLE (
    slot_id INTEGER,
    slot_position INTEGER,
    tier VARCHAR(20),
    event_id INTEGER,
    event_title VARCHAR(500),
    event_image VARCHAR(1000),
    event_start TIMESTAMP WITH TIME ZONE,
    event_city VARCHAR(255),
    event_venue VARCHAR(500),
    event_description TEXT,
    event_source_url VARCHAR(1000),
    event_price_tier VARCHAR(20),
    event_price_amount DECIMAL(10, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fs.id as slot_id,
        fs.slot_position,
        fs.tier,
        e.id as event_id,
        e.title as event_title,
        e.image_url as event_image,
        e.start_at as event_start,
        e.city as event_city,
        e.venue as event_venue,
        e.description as event_description,
        e.source_url as event_source_url,
        e.price_tier as event_price_tier,
        e.price_amount as event_price_amount
    FROM featured_slots fs
    INNER JOIN events e ON fs.event_id = e.id
    WHERE fs.is_active = TRUE
      AND fs.payment_status = 'PAID'
      AND NOW() BETWEEN fs.starts_at AND fs.ends_at
      AND e.status = 'PUBLISHED'
      AND e.start_at >= NOW()
    ORDER BY fs.slot_position ASC;
END;
$$ LANGUAGE plpgsql;

-- 7. Create trigger to update events.is_featured
CREATE OR REPLACE FUNCTION update_event_featured_status()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE events 
        SET is_featured = TRUE,
            featured_tier = NEW.tier,
            featured_until = NEW.ends_at
        WHERE id = NEW.event_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE events 
        SET is_featured = FALSE,
            featured_tier = NULL,
            featured_until = NULL
        WHERE id = OLD.event_id
          AND NOT EXISTS (
              SELECT 1 FROM featured_slots 
              WHERE event_id = OLD.event_id 
                AND is_active = TRUE 
                AND payment_status = 'PAID'
          );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_event_featured ON featured_slots;
CREATE TRIGGER trigger_update_event_featured
AFTER INSERT OR UPDATE OR DELETE ON featured_slots
FOR EACH ROW
EXECUTE FUNCTION update_event_featured_status();

-- 8. Add helpful comments
COMMENT ON TABLE featured_slots IS 'Stores paid featured/sponsored event slot bookings';
COMMENT ON TABLE featured_pricing IS 'Pricing tiers and configuration for featured slots';
COMMENT ON COLUMN featured_slots.slot_position IS '1=Platinum (Top-Left), 2=Gold (Top-Right), 3=Silver (Bottom-Left), 4=Bronze (Bottom-Right)';

-- Done!
SELECT 'Featured Events System installed successfully!' as status;

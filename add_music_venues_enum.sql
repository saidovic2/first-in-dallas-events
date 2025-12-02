-- Add House of Blues and Factory Deep Ellum to source_type enum

ALTER TYPE event_source_type ADD VALUE IF NOT EXISTS 'HOUSE_OF_BLUES';
ALTER TYPE event_source_type ADD VALUE IF NOT EXISTS 'FACTORY_DEEP_ELLUM';

-- Verify the new values were added
SELECT unnest(enum_range(NULL::event_source_type)) AS source_type;

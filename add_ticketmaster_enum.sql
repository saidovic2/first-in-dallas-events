-- Add TICKETMASTER to event_source_type enum
-- Run this in Supabase SQL Editor BEFORE importing events

ALTER TYPE event_source_type ADD VALUE IF NOT EXISTS 'TICKETMASTER';

-- Verify it was added
SELECT unnest(enum_range(NULL::event_source_type)) AS source_type;

-- Add dallas_arboretum to the sourcetype enum
-- Run this in your Supabase SQL Editor

ALTER TYPE sourcetype ADD VALUE IF NOT EXISTS 'dallas_arboretum';

-- Verify the change
SELECT enum_range(NULL::sourcetype);

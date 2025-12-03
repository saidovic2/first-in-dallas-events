-- Delete all Dallas Library events from the database
-- Run this in Supabase SQL Editor

-- First, let's see how many we have
SELECT COUNT(*) as total_dallas_library_events 
FROM events 
WHERE source_type = 'DALLAS_LIBRARY';

-- Show a few examples
SELECT id, title, start_at, image_url
FROM events 
WHERE source_type = 'DALLAS_LIBRARY'
LIMIT 5;

-- Delete all Dallas Library events
DELETE FROM events 
WHERE source_type = 'DALLAS_LIBRARY';

-- Verify deletion
SELECT COUNT(*) as remaining_dallas_library_events 
FROM events 
WHERE source_type = 'DALLAS_LIBRARY';

-- Fix Event Status Issue
-- This updates all DRAFT events to PUBLISHED status
-- So they appear on the WordPress directory

-- Update all DRAFT events to PUBLISHED (only future events)
UPDATE events 
SET status = 'PUBLISHED'
WHERE status = 'DRAFT'
AND start_at >= NOW();

-- Check how many events were updated
SELECT 
    COUNT(*) as total_updated,
    'Events updated from DRAFT to PUBLISHED' as message
FROM events 
WHERE status = 'PUBLISHED';

-- Verify the fix
SELECT 
    status,
    COUNT(*) as count
FROM events
GROUP BY status
ORDER BY count DESC;

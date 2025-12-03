-- Update all PUBLISHED events to DRAFT status
-- This allows you to review them before publishing to WordPress

UPDATE events 
SET status = 'DRAFT' 
WHERE status = 'PUBLISHED';

-- Show the result
SELECT 
    status, 
    COUNT(*) as count 
FROM events 
GROUP BY status;

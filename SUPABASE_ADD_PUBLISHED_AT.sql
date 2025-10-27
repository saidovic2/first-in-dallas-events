-- Add published_at column to event_submissions table

ALTER TABLE event_submissions
ADD COLUMN IF NOT EXISTS published_at timestamptz;

-- Add index for faster queries
CREATE INDEX IF NOT EXISTS idx_event_submissions_published_at 
ON event_submissions(published_at);

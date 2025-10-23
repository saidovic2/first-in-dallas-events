-- Add completed_at column to tasks table
-- This fixes the progression bar issue in the Facebook sync

ALTER TABLE tasks ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE;

-- Update existing completed tasks to set completed_at = updated_at
UPDATE tasks 
SET completed_at = updated_at 
WHERE status IN ('done', 'failed') 
AND completed_at IS NULL;

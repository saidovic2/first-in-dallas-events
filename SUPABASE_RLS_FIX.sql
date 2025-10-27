-- Fix RLS policies for CMS to read event_submissions

-- First, let's create a policy that allows reading all submissions (for admin/CMS)
CREATE POLICY "Allow public read access to event_submissions for CMS"
ON event_submissions
FOR SELECT
TO anon
USING (true);

-- Also ensure authenticated users can read all submissions
CREATE POLICY "Allow authenticated read access to event_submissions"
ON event_submissions
FOR SELECT
TO authenticated
USING (true);

-- Allow service role to do everything (for admin operations)
CREATE POLICY "Service role can do everything on event_submissions"
ON event_submissions
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Fix Supabase Storage Permissions for Event Images
-- Run this in your Supabase SQL Editor

-- 1. Make sure the events bucket exists and is public
UPDATE storage.buckets 
SET public = true 
WHERE id = 'events';

-- 2. Drop existing policies if they exist (to recreate them)
DROP POLICY IF EXISTS "Public can view event images" ON storage.objects;
DROP POLICY IF EXISTS "Service role can upload event images" ON storage.objects;
DROP POLICY IF EXISTS "Service role can update event images" ON storage.objects;
DROP POLICY IF EXISTS "Service role can delete event images" ON storage.objects;

-- 3. Create policy for public read access (CRITICAL for displaying images)
CREATE POLICY "Public can view event images"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'events');

-- 4. Allow service role to upload images (for worker)
CREATE POLICY "Service role can upload event images"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id = 'events');

-- 5. Allow service role to update images
CREATE POLICY "Service role can update event images"
ON storage.objects FOR UPDATE
TO service_role
USING (bucket_id = 'events');

-- 6. Allow service role to delete images
CREATE POLICY "Service role can delete event images"
ON storage.objects FOR DELETE
TO service_role
USING (bucket_id = 'events');

-- Verify the setup
SELECT 
  id, 
  name, 
  public as "Is Public?" 
FROM storage.buckets 
WHERE id = 'events';

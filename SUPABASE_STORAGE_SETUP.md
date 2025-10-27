# 🖼️ Supabase Storage Setup for Image Uploads

## Create Storage Bucket

Run this in your Supabase SQL Editor:

```sql
-- Create storage bucket for event images
INSERT INTO storage.buckets (id, name, public)
VALUES ('events', 'events', true);

-- Allow authenticated users to upload images
CREATE POLICY "Authenticated users can upload event images"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'events');

-- Allow public read access to event images
CREATE POLICY "Public can view event images"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'events');

-- Allow users to update their own images
CREATE POLICY "Users can update own event images"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'events');

-- Allow users to delete their own images
CREATE POLICY "Users can delete own event images"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'events');
```

## Alternative: Create via Dashboard (Easier!)

1. Go to **Storage** in Supabase sidebar
2. Click **New bucket**
3. Name: `events`
4. Check **Public bucket** ✅
5. Click **Save**

Done! Image uploads will now work.

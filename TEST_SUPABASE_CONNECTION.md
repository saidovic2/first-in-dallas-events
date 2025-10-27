# Debug: Check Supabase Data

## Option 1: Check in Supabase Dashboard

1. Go to: https://supabase.com/dashboard/project/jwlvikkbcjrnzsvhyfgy
2. Click **Table Editor** in sidebar
3. Click **event_submissions** table
4. See if your 2 submissions are there

## Option 2: Check Browser Console

1. Open http://localhost:3000/submissions
2. Press F12 to open DevTools
3. Go to **Console** tab
4. Look for any errors

## If Submissions Are Missing in Supabase:

The submissions might have failed to save. Let's test by submitting a new event:

1. Go to http://localhost:3001/submit
2. Fill in a test event
3. Submit it
4. Check browser console for errors
5. Check Supabase Table Editor to see if it appears

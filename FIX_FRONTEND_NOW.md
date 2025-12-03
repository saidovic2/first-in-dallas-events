# 🚨 FRONTEND PROBLEM FOUND - Wrong API URL!

## The Problem

Your CMS frontend (Vercel) is configured to connect to:
```
https://wonderful-vibrancy-production.up.railway.app
```

But **wonderful-vibrancy is your WORKER service**, not your API!

The frontend needs to connect to **first-in-dallas-events** (your API service).

---

## ⚡ FIX IT NOW (5 minutes)

### Step 1: Get Correct API Domain from Railway

1. Go to **Railway Dashboard**
2. Click **first-in-dallas-events** service (the API, not worker)
3. Go to **Settings** tab
4. Scroll to **Networking** section
5. Look for the domain - should be something like:
   - `first-in-dallas-events-production.up.railway.app`
   - OR another domain listed there
6. If no domain exists, click **"Generate Domain"**
7. **Copy the full URL** (e.g., `https://first-in-dallas-events-production.up.railway.app`)

### Step 2: Test the API Domain

In PowerShell, test it works:
```powershell
# Replace YOUR-API-DOMAIN with the domain from step 1
curl "https://YOUR-API-DOMAIN.up.railway.app/health"
```

Should return: `{"status":"healthy"}`

If you get 404 or error, the domain isn't right or service crashed.

---

### Step 3: Update Vercel Environment Variable

#### Option A: Using Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Find your CMS project
3. Click on the project
4. Go to **Settings** tab
5. Click **"Environment Variables"** in left sidebar
6. Find `NEXT_PUBLIC_API_URL`
7. Click **"Edit"** (pencil icon)
8. Change value to: `https://YOUR-API-DOMAIN.up.railway.app`
   - **Example:** `https://first-in-dallas-events-production.up.railway.app`
   - **Do NOT include `/api` at the end!**
9. Click **"Save"**
10. Go to **Deployments** tab
11. Click **"Redeploy"** on latest deployment (three dots menu)
12. Wait 2-3 minutes for redeployment

#### Option B: Using Vercel CLI (If you have it)

```powershell
# In your project folder
vercel env add NEXT_PUBLIC_API_URL

# When prompted, enter: https://YOUR-API-DOMAIN.up.railway.app
# Select: Production, Preview, Development (all)

# Then redeploy
vercel --prod
```

---

### Step 4: Update Local .env.local (For local development)

Update your local file too:

```bash
# web/.env.local
NEXT_PUBLIC_API_URL=https://YOUR-API-DOMAIN.up.railway.app

# Supabase credentials (keep these as is)
NEXT_PUBLIC_SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0NjM3NzIsImV4cCI6MjA3NzAzOTc3Mn0.mRluKwZ2B0qg0Z8YGYCx4QRFMP5WwxiTef_olGDEJS4
```

---

### Step 5: Commit and Push Changes

```powershell
git add web/.env.local
git commit -m "Fix: Update frontend API URL to correct Railway domain"
git push
```

Vercel will auto-deploy after push.

---

### Step 6: Test Frontend

1. Wait 2-3 minutes for Vercel deployment
2. Go to your CMS URL (e.g., `https://your-cms.vercel.app`)
3. Login to dashboard
4. Go to **Sync** page
5. Click **"Sync Eventbrite Events"**
6. Should show success message and sync progress!

---

## Why This Matters

### API Service (first-in-dallas-events):
- Handles HTTP requests from frontend
- Has routes like `/api/events`, `/api/sync`, `/api/auth`
- Needs public domain for frontend to access

### Worker Service (wonderful-vibrancy):
- Runs background tasks
- Processes events from Redis queue
- Does NOT handle HTTP requests
- Does NOT need public domain

**Your frontend was trying to send requests to the Worker, which doesn't have API endpoints!**

---

## Architecture Diagram

```
Frontend (Vercel)
    ↓ HTTP requests
API Service (first-in-dallas-events) ← CORRECT!
    ↓ Creates tasks
Redis Queue
    ↓ Pulls tasks
Worker Service (wonderful-vibrancy)
    ↓ Fetches events
Eventbrite API
    ↓ Saves events
PostgreSQL Database
```

**Frontend must connect to API, NOT Worker!**

---

## Verification Checklist

After fixing:

- [ ] Railway API domain is correct (first-in-dallas-events)
- [ ] API /health endpoint returns {"status":"healthy"}
- [ ] Vercel environment variable updated
- [ ] Vercel redeployed successfully
- [ ] Local .env.local updated
- [ ] CMS sync button works
- [ ] Events appear in CMS dashboard
- [ ] Events appear on WordPress site

---

## Common Mistakes

### ❌ Wrong: Using Worker URL
```
NEXT_PUBLIC_API_URL=https://wonderful-vibrancy-production.up.railway.app
```

### ✅ Correct: Using API URL
```
NEXT_PUBLIC_API_URL=https://first-in-dallas-events-production.up.railway.app
```

### ❌ Wrong: Adding /api at the end
```
NEXT_PUBLIC_API_URL=https://your-api.up.railway.app/api
```

### ✅ Correct: No /api suffix
```
NEXT_PUBLIC_API_URL=https://your-api.up.railway.app
```

The code already adds `/api` when needed!

---

## Troubleshooting

### Problem: "API domain returns 404"

**Causes:**
1. Domain not generated in Railway
2. Service crashed
3. Wrong domain copied

**Fix:**
- Railway → first-in-dallas-events → Settings → Networking → Generate Domain
- Check deployment logs for errors
- Verify all environment variables set

### Problem: "Vercel still using old URL after update"

**Causes:**
1. Didn't redeploy after changing env var
2. Browser cache

**Fix:**
- Vercel → Deployments → Redeploy latest
- Clear browser cache or use incognito mode

### Problem: "Sync button still shows error"

**Causes:**
1. Vercel not redeployed yet
2. API not responding
3. Authentication issue

**Fix:**
- Wait for Vercel deployment to finish
- Test API /health endpoint
- Check browser console for error messages

---

## Quick Summary

**Problem:** Frontend pointing to Worker instead of API
**Solution:** Update `NEXT_PUBLIC_API_URL` in Vercel to use first-in-dallas-events domain
**Time:** 5 minutes
**Impact:** Fixes sync button, events display, entire CMS functionality

---

**DO THIS NOW:**
1. Get first-in-dallas-events domain from Railway
2. Update Vercel environment variable
3. Redeploy on Vercel
4. Test sync button

**After this fix, your CMS will work!** 🎉

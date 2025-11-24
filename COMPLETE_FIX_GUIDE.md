# 🔧 Complete Fix Guide for Events CMS

## Issues Identified & Fixed

### Issue 1: Railway Deployment Failures ❌
**Problem:** Both services failing with "Error creating build plan with Nixpacks"

**Root Cause:** Railway couldn't detect how to build the services

**Solution:** Created `railway.toml` configuration files to force Docker builds

### Issue 2: Events Not Showing on WordPress ❌
**Problem:** 
- Events sync from Eventbrite works
- Events saved to database
- But WordPress directory shows nothing (or old events)

**Root Cause:** Worker saves events with status="DRAFT" but WordPress requests status="PUBLISHED"

**Solution:** Changed worker to save events as "PUBLISHED" by default

---

## 🚀 Step-by-Step Fix Instructions

### Step 1: Update Existing Events in Database

You need to update existing DRAFT events to PUBLISHED status.

**Option A: Via Railway Dashboard (Recommended)**

1. Go to Railway Dashboard → Your Project
2. Click on **PostgreSQL** service
3. Click **"Connect"** → Copy connection command
4. Click **"Query"** or open a PostgreSQL client
5. Run this SQL:

```sql
UPDATE events 
SET status = 'PUBLISHED'
WHERE status = 'DRAFT'
AND start_at >= NOW();
```

**Option B: Run SQL Script Locally**

If you have Railway CLI installed:

```powershell
# In your project directory
railway run psql $DATABASE_URL -f FIX_EVENT_STATUS.sql
```

### Step 2: Push Code Changes to GitHub

All the fixes have been committed. Now push to GitHub:

```powershell
# Stage all changes
git add .

# Commit
git commit -m "Fix Railway deployment and event status issues"

# Push to trigger Railway redeployment
git push origin main
```

### Step 3: Monitor Railway Deployment

1. Go to Railway Dashboard
2. Watch both services deploy:
   - **first-in-dallas-events** (API)
   - **wonderful-vibrancy** (Worker - or whatever your worker is named)

3. **Check API Logs** - Should see:
   ```
   ✅ Database tables created/verified
   Database initialization complete!
   Uvicorn running on http://0.0.0.0:xxxx
   ```

4. **Check Worker Logs** - Should see:
   ```
   Worker started. Waiting for tasks...
   ```

### Step 4: Verify Railway Environment Variables

Make sure these are set in **both API and Worker services**:

**Required Variables:**
```
DATABASE_URL=<railway-postgres-url>
REDIS_URL=<railway-redis-url>
JWT_SECRET=<any-random-secret-string>
EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C
TICKETMASTER_API_KEY=Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK
TICKETMASTER_AFFILIATE_ID=6497023
SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-supabase-key>
```

**Where to add:**
1. Railway Dashboard → Select Service
2. **Variables** tab
3. Add each variable
4. Service will redeploy automatically

### Step 5: Update WordPress Plugin Settings

1. Login to WordPress admin
2. Go to **Settings → Events CMS**
3. Update **Events CMS API URL** to your Railway API URL:
   ```
   https://your-api-name.up.railway.app/api
   ```
   (Get this from Railway → API Service → Settings → Networking → Domain)

4. Click **Save Changes**

### Step 6: Test Event Sync

1. Go to your CMS Dashboard (Railway web service or local)
2. Navigate to **Sync** page
3. Click **"🎫 Sync Eventbrite Events"**
4. Wait 30-60 seconds
5. Go to **Events** page
6. You should see new events with status="PUBLISHED"

### Step 7: Verify WordPress Directory

1. Go to your WordPress site
2. Visit the Events page (where you have `[events_directory]` shortcode)
3. **You should now see events!**

---

## 🐛 Troubleshooting

### Railway Deployment Still Failing?

**Check Build Logs:**
1. Railway Dashboard → Service → Deployments → Click on failed deployment
2. Read error messages
3. Common issues:
   - Missing environment variables
   - Database connection failed
   - Port binding issues

**Verify Railway Configuration:**
```
Each service should have:
- Root Directory: /api (or /worker)
- Dockerfile Path: Dockerfile  
- Builder: DOCKERFILE (from railway.toml)
```

### Events Still Not Showing on WordPress?

**1. Check API Connection:**
```bash
# Replace with your Railway API URL
curl https://your-api.railway.app/health
```
Should return: `{"status": "healthy"}`

**2. Check Events Endpoint:**
```bash
curl "https://your-api.railway.app/api/events?status=PUBLISHED&limit=5"
```
Should return JSON array of events

**3. Check WordPress Plugin:**
- Settings → Events CMS → Verify API URL is correct
- Try adding `/api/events?limit=10` to the end and visit in browser
- Should see JSON, not error

**4. Check Event Status in Database:**
```sql
SELECT status, COUNT(*) 
FROM events 
GROUP BY status;
```
Should show PUBLISHED events, not just DRAFT

### CMS Can't Sync from Eventbrite?

**1. Check Environment Variable:**
```powershell
# In Railway dashboard
EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C
```

**2. Check Worker Logs:**
- Should see: "Syncing events from Eventbrite organizer: ..."
- If error, check API token validity

**3. Test Eventbrite API Token:**
```bash
curl -H "Authorization: Bearer MOZFNTBR4O22QQV33X2C" \
  "https://www.eventbriteapi.com/v3/organizers/18169391630/events/"
```
Should return events JSON

---

## 📊 Verification Checklist

After following all steps, verify:

- [ ] Railway API service is deployed and running
- [ ] Railway Worker service is deployed and running  
- [ ] PostgreSQL and Redis services are connected
- [ ] Environment variables are set in both services
- [ ] API health check works: `/health` returns {"status": "healthy"}
- [ ] Events endpoint works: `/api/events?status=PUBLISHED` returns events
- [ ] WordPress plugin settings have correct Railway API URL
- [ ] WordPress Events page shows events
- [ ] Can sync new events from Eventbrite
- [ ] New events appear on WordPress within 1 minute

---

## 📝 Summary of All Changes Made

### Files Created:
1. `api/railway.toml` - Railway configuration for API service
2. `worker/railway.toml` - Railway configuration for Worker service  
3. `web/railway.toml` - Railway configuration for Web/CMS service
4. `FIX_EVENT_STATUS.sql` - SQL script to update DRAFT → PUBLISHED
5. `RAILWAY_DEPLOYMENT_FIX.md` - Detailed Railway deployment guide
6. `COMPLETE_FIX_GUIDE.md` - This file

### Files Modified:
1. `api/Dockerfile` - Added PORT configuration
2. `worker/Dockerfile` - Added Python optimization flags
3. `worker/worker.py` - Changed event status from DRAFT → PUBLISHED (line 129)

### Database Changes:
- Updated existing DRAFT events to PUBLISHED status

---

## 🎉 Expected Results

After completing this guide:

1. ✅ Railway services deploy successfully
2. ✅ Events sync from Eventbrite works
3. ✅ Events are saved as PUBLISHED (not DRAFT)
4. ✅ WordPress directory shows current events
5. ✅ Old/past events are automatically filtered out
6. ✅ New events appear on WordPress within 1 minute of sync

---

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. **Check Service Logs in Railway:**
   - API logs for errors
   - Worker logs for sync status
   - PostgreSQL connection logs

2. **Verify Database Connection:**
   ```bash
   railway run bash
   echo $DATABASE_URL
   ```

3. **Test Locally First:**
   ```powershell
   # Start local services
   docker-compose up
   
   # Test sync
   # Open http://localhost:3001
   # Click Sync Eventbrite
   ```

4. **WordPress Debug Mode:**
   Add to `wp-config.php`:
   ```php
   define('WP_DEBUG', true);
   define('WP_DEBUG_LOG', true);
   ```
   Check `wp-content/debug.log` for errors

---

## 📞 Quick Reference

**Railway Dashboard:** https://railway.app/dashboard  
**Your Project:** Check Railway for project URL  
**API Health:** `https://your-api.railway.app/health`  
**Events API:** `https://your-api.railway.app/api/events?status=PUBLISHED`  
**WordPress Settings:** WP Admin → Settings → Events CMS

---

**You should now have a fully working Events CMS!** 🎊

If everything is working:
1. Sync some events from Eventbrite
2. Visit your WordPress site
3. See events appear automatically
4. Celebrate! 🎉

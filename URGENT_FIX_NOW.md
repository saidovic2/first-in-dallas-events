# 🚨 URGENT FIX - Railway API Not Found

## Problem
Your Railway API domain has changed or is incorrect. The old URL doesn't work.

## ⚡ QUICK FIX (5 minutes)

### Step 1: Find Your Railway API Domain

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click on your **API service** (first-in-dallas-events or similar)
3. Go to **Settings** tab → **Networking** section
4. Look for **Public Domain** or **Generate Domain** button
5. Copy the full URL (e.g., `https://something-production-xyz.up.railway.app`)

### Step 2: Test Your Railway API

Once you have the domain, test it in PowerShell:

```powershell
# Replace with YOUR actual Railway domain
$RAILWAY_API = "https://your-actual-domain.up.railway.app"

# Test health endpoint
curl "$RAILWAY_API/health"
# Should return: {"status":"healthy"}

# Test events endpoint  
curl "$RAILWAY_API/api/events?limit=5"
# Should return: JSON array of events
```

### Step 3: Update WordPress Plugin

1. Login to **WordPress Admin**
2. Go to **Settings → Events CMS**
3. Update **Events CMS API URL** to:
   ```
   https://your-actual-railway-domain.up.railway.app/api
   ```
   ⚠️ **IMPORTANT:** Add `/api` at the end!
4. Click **Save Changes**

### Step 4: Verify Railway Services Are Running

In Railway Dashboard, check:
- ✅ **API Service** - Status should be "Active" (green)
- ✅ **Worker Service** - Status should be "Active" (green)
- ✅ **PostgreSQL** - Running
- ✅ **Redis** - Running

If any service shows "Crashed" or "Building":
- Wait 2-3 minutes for deployment to complete
- Check **Logs** tab for errors

### Step 5: Update Database (CRITICAL!)

Once API is active, run this SQL in Railway:

1. Railway → **PostgreSQL** service → **Query** tab
2. Run:
```sql
-- Update all DRAFT events to PUBLISHED
UPDATE events 
SET status = 'PUBLISHED'
WHERE status = 'DRAFT';

-- Verify count
SELECT status, COUNT(*) 
FROM events 
WHERE start_at >= NOW()
GROUP BY status;
```

### Step 6: Check Environment Variables

In Railway, verify **BOTH API and Worker** have these variables set:

**API Service:**
```
DATABASE_URL=<from Railway PostgreSQL>
REDIS_URL=<from Railway Redis>
JWT_SECRET=any-random-string-here
EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C
TICKETMASTER_API_KEY=Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK
TICKETMASTER_AFFILIATE_ID=6497023
SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-key>
```

**Worker Service:**
Same variables as API

---

## 🔍 Troubleshooting

### Issue: Railway API URL is 404
**Solution:** 
- The domain changed after redeployment
- Go to Railway → API Service → Settings → Networking
- Copy the new domain
- Update WordPress settings

### Issue: No events showing on WordPress
**Causes:**
1. ❌ WordPress has wrong API URL → Fix in Step 3
2. ❌ Events are DRAFT status → Fix in Step 5 (SQL update)
3. ❌ API service crashed → Check Railway logs

### Issue: Can't sync from Eventbrite
**Causes:**
1. ❌ EVENTBRITE_API_TOKEN not set → Add to Railway variables
2. ❌ Worker service not running → Check Railway worker status
3. ❌ Redis not connected → Verify REDIS_URL is set

---

## 📊 Verification Checklist

After completing all steps:

```powershell
# 1. Test API health
curl "https://YOUR-DOMAIN.up.railway.app/health"
# Expected: {"status":"healthy"}

# 2. Test events endpoint
curl "https://YOUR-DOMAIN.up.railway.app/api/events?status=PUBLISHED&limit=5"
# Expected: JSON array with events

# 3. Check event count
curl "https://YOUR-DOMAIN.up.railway.app/api/stats"
# Should show event statistics
```

Then:
- ✅ Visit WordPress Events page
- ✅ Should see current events (not old ones)
- ✅ Old events (before today) should be filtered out

---

## 🚨 If Still Not Working

### Check Railway Deployment Logs:

1. Railway → API Service → **Deployments** tab
2. Click latest deployment
3. Check for errors like:
   - Database connection failed
   - Missing environment variables
   - Port binding errors

### Check WordPress Debug:

Add to `wp-config.php`:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

Then check `wp-content/debug.log` for API errors.

---

## 📞 Most Common Issue: Wrong Railway Domain

The URL `https://first-in-dallas-events-production.up.railway.app` might not be your actual domain.

**Find correct domain:**
1. Railway Dashboard
2. Click API service
3. Settings → Networking → Domain

**It might look like:**
- `https://astonishing-warmth-production.up.railway.app`
- `https://wonderful-vibrancy-production.up.railway.app`
- Or something else entirely

**Update WordPress with the CORRECT domain + /api**

---

## ⚡ Quick Command Reference

```powershell
# Find Railway domain (if you have Railway CLI)
railway status

# Test API
curl "https://YOUR-DOMAIN/health"

# Check events
curl "https://YOUR-DOMAIN/api/events?limit=10"

# Local testing
docker-compose up
```

---

**Next Action:** Go to Railway Dashboard and find your actual API domain, then update WordPress settings with that domain + `/api`

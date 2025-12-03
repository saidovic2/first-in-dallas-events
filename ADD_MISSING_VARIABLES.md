# Add Missing Environment Variables

You're very close! Just need to add a few more variables.

---

## Missing Variables

### 1. Add to first-in-dallas-events (API):

```
JWT_SECRET = my-secret-key-change-this-12345
```

**How to add:**
1. Railway → first-in-dallas-events → Variables tab
2. Click "+ New Variable"
3. Variable name: `JWT_SECRET`
4. Value: `my-secret-key-change-this-12345`
5. Click "Add"

---

### 2. Add to wonderful-vibrancy (Worker):

```
EVENTBRITE_API_TOKEN = MOZFNTBR4O22QQV33X2C
SUPABASE_URL = https://jwlvikkbcjrnzsvhyfgy.supabase.co
SUPABASE_SERVICE_ROLE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTQ2Mzc3MiwiZXhwIjoyMDc3MDM5NzcyfQ.hw6S9WncejbjqQG13hR3AYtFbldw3H5miuLQHpy6NIY
```

**How to add:**
1. Railway → wonderful-vibrancy → Variables tab
2. Click "+ New Variable" for each:
   - Variable name: `EVENTBRITE_API_TOKEN`, Value: `MOZFNTBR4O22QQV33X2C`
   - Variable name: `SUPABASE_URL`, Value: `https://jwlvikkbcjrnzsvhyfgy.supabase.co`
   - Variable name: `SUPABASE_SERVICE_ROLE_KEY`, Value: (the long key above)
3. Click "Add" for each

---

## Check Deployment Logs

After adding variables, services will redeploy. To see logs:

### For API (first-in-dallas-events):
1. Click first-in-dallas-events service
2. Click "Deployments" tab
3. Click latest deployment
4. Scroll through logs - look for errors

### For Worker (wonderful-vibrancy):
1. Click wonderful-vibrancy service
2. Click "Deployments" tab  
3. Click latest deployment
4. Scroll through logs

---

## Common Log Errors You Might See

### Error: "No module named 'xyz'"
**Meaning:** Missing Python package
**Fix:** Check requirements.txt includes the package

### Error: "Connection refused" or "Database connection failed"
**Meaning:** Wrong DATABASE_URL or database not accessible
**Fix:** Verify DATABASE_URL is correct from Postgres service

### Error: "Redis connection failed"
**Meaning:** Wrong REDIS_URL
**Fix:** Verify REDIS_URL is correct from Redis service

### Success: "✅ Database tables created/verified"
**Meaning:** API connected to database successfully!

### Success: "Worker started, listening for tasks..."
**Meaning:** Worker is running and waiting for sync tasks!

---

## After Adding Variables

1. Wait 1-2 minutes for redeployment
2. Check both services show green checkmarks
3. Check deployment logs for any errors
4. Test API health endpoint

---

## Test API After Variables Added

In PowerShell:
```powershell
# First, get your API domain from Railway
# Settings → Networking → Copy domain

# Test health
curl "https://YOUR-DOMAIN.up.railway.app/health"
# Should return: {"status":"healthy"}

# Test events
curl "https://YOUR-DOMAIN.up.railway.app/api/events?limit=5"
# Should return: JSON array
```

---

## What Happens When You Click Sync

1. **CMS Dashboard** sends request to Railway API: `POST /api/sync/eventbrite`
2. **API Service** receives request and creates a task
3. **API Service** puts task in Redis queue
4. **Worker Service** pulls task from Redis queue
5. **Worker Service** calls Eventbrite API to fetch events
6. **Worker Service** uploads images to Supabase
7. **Worker Service** saves events to PostgreSQL database
8. **Worker Service** updates task status to "completed"
9. **CMS Dashboard** shows success message

**If sync fails, it's usually because:**
- Worker missing EVENTBRITE_API_TOKEN (can't call Eventbrite)
- Worker missing SUPABASE keys (can't upload images)
- Worker can't connect to database or Redis

---

## Next Steps

1. ✅ Add JWT_SECRET to API
2. ✅ Add 3 missing variables to Worker
3. ✅ Wait for redeployment (1-2 min)
4. ✅ Check deployment logs for errors
5. ✅ Get API domain from Settings → Networking
6. ✅ Test API /health endpoint
7. ✅ Update WordPress with API URL
8. ✅ Try sync again!

---

**After adding these variables, your sync button should work!**

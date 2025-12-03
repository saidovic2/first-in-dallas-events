# Your Services Are Deployed - Here's What to Do Next

## Current Status
✅ Railway services deployed (green checkmarks)
❌ API not accessible (404 errors)
❌ Sync button not working
❌ CMS directory empty

---

## Why This Is Happening

Your services deployed successfully from GitHub, but they need:
1. **Public domain generated** (so you can access the API)
2. **Environment variables** (DATABASE_URL, REDIS_URL, etc.)
3. **WordPress configured** with correct API URL
4. **Database events** updated from DRAFT to PUBLISHED

---

## DO THIS NOW (10 minutes total)

### 1. Add Environment Variables to API Service (5 min)

Go to Railway Dashboard:

1. Click **first-in-dallas-events** service
2. Click **Variables** tab  
3. Click **"+ New Variable"** and add each of these:

```
DATABASE_URL = <Click Postgres service → Variables → Copy connection string>
REDIS_URL = <Click Redis service → Variables → Copy connection string>
JWT_SECRET = my-secret-key-12345
EVENTBRITE_API_TOKEN = MOZFNTBR4O22QQV33X2C
TICKETMASTER_API_KEY = Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK
TICKETMASTER_AFFILIATE_ID = 6497023
SUPABASE_URL = https://jwlvikkbcjrnzsvhyfgy.supabase.co
SUPABASE_SERVICE_ROLE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTQ2Mzc3MiwiZXhwIjoyMDc3MDM5NzcyfQ.hw6S9WncejbjqQG13hR3AYtFbldw3H5miuLQHpy6NIY
```

**How to get DATABASE_URL:**
- Click Postgres service
- Go to Variables tab or Connect tab
- Copy the connection string (starts with `postgresql://`)

**How to get REDIS_URL:**
- Click Redis service  
- Go to Variables tab
- Copy the connection string (starts with `redis://`)

4. Service will auto-redeploy after adding variables (wait 1-2 min)

---

### 2. Add Same Variables to Worker Service (2 min)

1. Click **wonderful-vibrancy** service
2. Click **Variables** tab
3. Add the **SAME 8 variables** as above

---

### 3. Generate Public Domain for API (1 min)

1. Click **first-in-dallas-events** service
2. Go to **Settings** tab
3. Find **"Networking"** section
4. Click **"Generate Domain"** if no domain exists
5. **Copy the domain URL**
   - Example: `first-in-dallas-events-production.up.railway.app`

---

### 4. Test API is Working (30 seconds)

In PowerShell:
```powershell
# Replace YOUR-DOMAIN with the domain from step 3
curl "https://YOUR-DOMAIN.up.railway.app/health"
```

Should return: `{"status":"healthy"}`

---

### 5. Update WordPress (1 min)

1. WordPress Admin → **Settings → Events CMS**
2. **Events CMS API URL:** `https://YOUR-DOMAIN.up.railway.app/api`
3. **Save Changes**

---

### 6. Fix Database Events (1 min)

Railway → **Postgres** service → **Query** tab:

```sql
UPDATE events 
SET status = 'PUBLISHED'
WHERE status = 'DRAFT';
```

Click "Run" or "Execute"

---

### 7. Test Everything

1. **CMS Dashboard:** Go to Sync page → Click "Sync Eventbrite Events"
2. **CMS Events:** Should show events
3. **WordPress:** Visit Events page → Should show current events

---

## Quick Reference

| Task | Where | What to Do |
|------|-------|------------|
| Add variables | Railway → Service → Variables | Add 8 env vars |
| Generate domain | Railway → Service → Settings → Networking | Generate Domain |
| Update WordPress | WP Admin → Settings → Events CMS | Set API URL |
| Fix database | Railway → Postgres → Query | Run UPDATE SQL |

---

## Troubleshooting

### Service keeps crashing after adding variables
- Check deployment logs for specific error
- Usually wrong DATABASE_URL or REDIS_URL format

### API still returns 404
- Make sure you generated public domain
- Check service status is "Active" (green)

### Sync button still shows error
- Verify WordPress has correct API URL
- Check API /health endpoint returns healthy

### CMS directory still empty
- Run database UPDATE to change DRAFT to PUBLISHED
- Try syncing from Eventbrite again

---

## Most Important Step

**#1 - Add environment variables!**

Without DATABASE_URL and REDIS_URL, the services cannot connect to the database and will not work properly.

---

**Detailed guides available:**
- `FIX_NOW_SIMPLE.txt` - Simple text instructions
- `RAILWAY_CHECKLIST.md` - Complete checklist with troubleshooting

**After completing all steps, your CMS will sync events and display them on WordPress!**

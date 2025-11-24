# 🔧 Railway Manual Configuration (No railway.toml)

Railway was confused by multiple railway.toml files. I've removed them.
Now you need to configure EACH service manually in Railway Dashboard.

---

## 🎯 SERVICE 1: first-in-dallas-events (API)

### Step 1: Click on first-in-dallas-events service

### Step 2: Go to Settings tab

### Step 3: Click "Source" in left sidebar

Look for **"Source Settings"** and set:
- **Watch Paths:** Leave empty OR set to `api/**`

### Step 4: Scroll to "Build" section

You should see **"Dockerfile"** with a blue link.

**Click the "Dockerfile" link dropdown** and you'll see:
- Root Directory field
- Custom Dockerfile Path

Set these:
```
Root Directory: api
Custom Dockerfile Path: Dockerfile
```

OR if there's a **"Build Command"** field instead, leave it empty.

### Step 5: Check "Deploy" section

Should have:
```
Start Command: sh -c 'python init_db.py && uvicorn main:app --host 0.0.0.0 --port $PORT'
```

If empty, Railway will use CMD from Dockerfile (which is correct).

### Step 6: Save and Redeploy

1. Changes auto-save
2. Go to **Deployments** tab
3. Click **"Redeploy"** button on latest deployment

---

## 🎯 SERVICE 2: wonderful-vibrancy (Worker)

### Step 1: Click on wonderful-vibrancy service

### Step 2: Go to Settings tab

### Step 3: Click "Source" in left sidebar

Set:
- **Watch Paths:** Leave empty OR set to `worker/**`

### Step 4: Scroll to "Build" section

Click the **"Dockerfile"** link dropdown and set:
```
Root Directory: worker
Custom Dockerfile Path: Dockerfile
```

### Step 5: Check "Deploy" section

Should have:
```
Start Command: python worker.py
```

If empty, Railway will use CMD from Dockerfile (which is correct).

### Step 6: Save and Redeploy

1. Changes auto-save
2. Go to **Deployments** tab
3. Click **"Redeploy"** button

---

## ⚠️ IMPORTANT: Environment Variables

**BOTH services need these variables set:**

### How to Add Variables:
1. Click service
2. Go to **Variables** tab
3. Click **"+ New Variable"**
4. Add each one below

### Required Variables:

```plaintext
DATABASE_URL=<copy from PostgreSQL service>
REDIS_URL=<copy from Redis service>
JWT_SECRET=your-random-secret-key-here
EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C
TICKETMASTER_API_KEY=Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK
TICKETMASTER_AFFILIATE_ID=6497023
SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTQ2Mzc3MiwiZXhwIjoyMDc3MDM5NzcyfQ.hw6S9WncejbjqQG13hR3AYtFbldw3H5miuLQHpy6NIY
```

### To get DATABASE_URL and REDIS_URL:
1. Click on **PostgreSQL** service → Variables tab → Copy connection string
2. Click on **Redis** service → Variables tab → Copy connection string

---

## 📊 After Both Services Are "Active"

### 1. Get API Domain
1. Click **first-in-dallas-events** service
2. Go to **Settings** → **Networking**
3. Click **"Generate Domain"** if no domain exists
4. Copy the URL

### 2. Test API
```powershell
curl "https://your-railway-domain.up.railway.app/health"
```
Should return: `{"status":"healthy"}`

### 3. Test Events
```powershell
curl "https://your-railway-domain.up.railway.app/api/events?limit=5"
```
Should return: JSON array of events

---

## 🌐 Update WordPress

1. WordPress Admin → **Settings → Events CMS**
2. **Events CMS API URL:** `https://your-railway-domain.up.railway.app/api`
3. **Save Changes**

---

## 💾 Fix Database

Railway → **PostgreSQL** service → **Query** tab:

```sql
-- Update all DRAFT events to PUBLISHED
UPDATE events 
SET status = 'PUBLISHED'
WHERE status = 'DRAFT'
AND start_at >= NOW();

-- Verify
SELECT status, COUNT(*) 
FROM events 
WHERE start_at >= NOW()
GROUP BY status;
```

---

## ✅ Verification Checklist

After configuration:

- [ ] Both services show "Active" (green) in Railway
- [ ] API responds to /health endpoint
- [ ] Events endpoint returns JSON array
- [ ] WordPress has correct API URL
- [ ] Database events are PUBLISHED status
- [ ] WordPress Events page shows current events
- [ ] Old events (before today) filtered out

---

## 🐛 Troubleshooting

### Service Still Shows "Dockerfile does not exist"

**Cause:** Root Directory not set correctly

**Fix:**
1. Settings → Build section
2. Click "Dockerfile" blue link/dropdown
3. Set Root Directory to `api` or `worker`
4. Redeploy

### Service Crashes with "DATABASE_URL not set"

**Cause:** Environment variables missing

**Fix:**
1. Variables tab → Add DATABASE_URL
2. Copy from PostgreSQL service
3. Service auto-redeploys

### API Returns 502 Bad Gateway

**Cause:** Service crashed or still starting

**Fix:**
1. Check Deployments → View Logs
2. Look for specific error
3. Usually missing environment variable

### WordPress Shows No Events

**Causes & Fixes:**
1. ❌ Wrong API URL → Update in WordPress settings
2. ❌ Events are DRAFT → Run SQL to update to PUBLISHED
3. ❌ API not responding → Check Railway service status

---

## 📝 Configuration Summary

| Service | Root Directory | Dockerfile Path | Start Command |
|---------|---------------|-----------------|---------------|
| **first-in-dallas-events** | `api` | `Dockerfile` | Auto from Dockerfile |
| **wonderful-vibrancy** | `worker` | `Dockerfile` | Auto from Dockerfile |

**Both services need the SAME environment variables!**

---

## 🎯 Quick Steps

1. ✅ Configure first-in-dallas-events: Root Dir = `api`
2. ✅ Configure wonderful-vibrancy: Root Dir = `worker`
3. ✅ Add environment variables to BOTH
4. ✅ Redeploy both services
5. ✅ Wait for "Active" status
6. ✅ Get API domain
7. ✅ Update WordPress
8. ✅ Fix database (DRAFT → PUBLISHED)

**Total time: 10 minutes**

---

## ⚠️ Why We Removed railway.toml

Railway was confused because:
- Multiple railway.toml files in project
- Railway reading wrong railway.toml for each service
- Manual Dashboard config is more reliable for monorepos

**Dashboard configuration overrides railway.toml anyway!**

---

**NOW: Go configure both services in Railway Dashboard as shown above!**

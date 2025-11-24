# 🚨 CRITICAL: Railway Dashboard Configuration Required

## The Problem
Railway services are failing with **"Dockerfile does not exist"** because the **Root Directory** is not configured in Railway Dashboard.

The `railway.toml` files exist, but Railway needs you to **manually set the Root Directory** for each service.

---

## ⚡ IMMEDIATE FIX (5 minutes)

### Step 1: Configure API Service (first-in-dallas-events)

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click your project
3. Click **"first-in-dallas-events"** service
4. Click **"Settings"** tab
5. Scroll to **"Build"** section
6. Set these EXACT values:

```
Root Directory: api
Dockerfile Path: Dockerfile
Builder: DOCKERFILE
```

**Screenshot of what to set:**
- **Root Directory:** `api` (no leading slash)
- **Dockerfile Path:** `Dockerfile` (exactly as shown)
- **Builder:** Select "DOCKERFILE" from dropdown

7. Click **"Save"** or it auto-saves
8. Go to **"Deployments"** tab
9. Click **"Redeploy"** button

### Step 2: Configure Worker Service (wonderful-vibrancy)

1. Still in Railway Dashboard
2. Click **"wonderful-vibrancy"** service (or your worker service name)
3. Click **"Settings"** tab
4. Scroll to **"Build"** section
5. Set these EXACT values:

```
Root Directory: worker
Dockerfile Path: Dockerfile
Builder: DOCKERFILE
```

6. Click **"Save"**
7. Go to **"Deployments"** tab
8. Click **"Redeploy"** button

### Step 3: Wait for Deployment (2-3 minutes)

Both services will now rebuild. Watch for:
- ✅ "Building..." → "Deploying..." → "Active" (green)
- ❌ If fails, check logs (see troubleshooting below)

---

## 📋 Environment Variables Check

While services are building, verify **BOTH services** have these variables:

### For API Service:
1. Railway → first-in-dallas-events → **Variables** tab
2. Add if missing:

```
DATABASE_URL=<copy from PostgreSQL service>
REDIS_URL=<copy from Redis service>
JWT_SECRET=your-secret-key-change-this
EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C
TICKETMASTER_API_KEY=Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK
TICKETMASTER_AFFILIATE_ID=6497023
SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTQ2Mzc3MiwiZXhwIjoyMDc3MDM5NzcyfQ.hw6S9WncejbjqQG13hR3AYtFbldw3H5miuLQHpy6NIY
```

### For Worker Service:
1. Railway → wonderful-vibrancy → **Variables** tab
2. Add SAME variables as API service

**To get DATABASE_URL and REDIS_URL:**
- Click on PostgreSQL service → Copy connection string
- Click on Redis service → Copy connection string

---

## ✅ After Services Are Active

### 1. Get API Domain
1. Railway → first-in-dallas-events service
2. **Settings** tab → **Networking** section
3. If no domain shown, click **"Generate Domain"**
4. Copy the domain (e.g., `https://something-production.up.railway.app`)

### 2. Test API
```powershell
# Replace with your actual domain
curl "https://your-domain.up.railway.app/health"
```
Should return: `{"status":"healthy"}`

### 3. Update WordPress
1. WordPress Admin → **Settings → Events CMS**
2. API URL: `https://your-domain.up.railway.app/api`
3. Save Changes

### 4. Fix Database
Railway → PostgreSQL → **Query** tab:
```sql
UPDATE events 
SET status = 'PUBLISHED'
WHERE status = 'DRAFT'
AND start_at >= NOW();
```

---

## 🐛 Troubleshooting

### Error: "No such file or directory: 'requirements.txt'"
**Fix:** Root Directory not set correctly
- Must be `api` for API service
- Must be `worker` for Worker service

### Error: "DATABASE_URL is not set"
**Fix:** Add environment variables (see checklist above)

### Error: "Port already in use"
**Fix:** Already fixed in Dockerfile - just redeploy

### Services Still Show "Building" After 5 Minutes
**Fix:** 
1. Click on service → Deployments → View logs
2. Look for specific error
3. Usually missing environment variable

---

## 📸 Visual Guide

### Where to Set Root Directory:
```
Railway Dashboard
  → Select Service (e.g., first-in-dallas-events)
    → Settings Tab
      → Scroll to "Build" section
        → Find "Root Directory" field
          → Enter: api (for API service)
          → Enter: worker (for Worker service)
```

### Where to Set Dockerfile Path:
```
Same "Build" section as above
  → Find "Dockerfile Path" field
    → Enter: Dockerfile
```

### Where to Set Builder:
```
Same "Build" section
  → Find "Builder" dropdown
    → Select: DOCKERFILE
```

---

## 🎯 Summary

**The ONLY thing preventing deployment:**
- Root Directory not configured in Railway Dashboard

**Fix:**
1. API service → Settings → Build → Root Directory: `api`
2. Worker service → Settings → Build → Root Directory: `worker`
3. Both services → Dockerfile Path: `Dockerfile`
4. Both services → Builder: `DOCKERFILE`
5. Redeploy both services

**Then:**
6. Add environment variables
7. Get API domain
8. Update WordPress
9. Fix database (DRAFT → PUBLISHED)

**Total time: 5-10 minutes**

---

## ⚠️ Critical Notes

- ✅ Dockerfile EXISTS in both api/ and worker/ folders
- ✅ railway.toml files EXISTS and are correct
- ❌ Railway Dashboard settings NOT configured (this is the problem)
- ❌ Root Directory MUST be set manually in Dashboard

**Railway cannot automatically detect subdirectories without Root Directory setting!**

---

## 🚀 After Everything Works

You should see:
- ✅ Railway services "Active" (green)
- ✅ API responds to /health
- ✅ Events sync from Eventbrite
- ✅ WordPress shows current events
- ✅ Old events filtered out

---

**DO THIS NOW:**
1. Open Railway Dashboard
2. Configure Root Directory for BOTH services
3. Redeploy
4. Wait 2-3 minutes
5. Check this guide for next steps

**You MUST configure Railway Dashboard manually. The railway.toml files alone are not enough!**

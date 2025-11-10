# 🔑 Environment Variables Setup - COMPLETE GUIDE

## 🎯 **What You Need to Configure**

You need to set environment variables in **TWO places**:

1. ☁️ **Railway** (your API backend)
2. 🌐 **Vercel** (your Admin CMS frontend)

---

## ☁️ **PART 1: Railway (API Backend)**

### **Where to Add:**
1. Go to: https://railway.app
2. Select your project: **wonderful-vibrancy-production**
3. Click on your **API service** (the one running your FastAPI)
4. Go to: **Variables** tab
5. Click **"+ New Variable"**

### **Variables to Add:**

```bash
# Ticketmaster API
TICKETMASTER_API_KEY=Tx3dcKeerAsHFOrhBsO6JVK2HbT0AEoK
TICKETMASTER_AFFILIATE_ID=6497023

# Eventbrite API
EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C

# Supabase (for image storage)
SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTQ2Mzc3MiwiZXhwIjoyMDc3MDM5NzcyfQ.hw6S9WncejbjqQG13hR3AYtFbldw3H5miuLQHpy6NIY

# Database (should already be there)
DATABASE_URL=postgresql://...  # (already configured by Railway)

# Redis (for worker queue)
REDIS_URL=redis://...  # (check if this exists, if not add Redis service)
```

### **After Adding Variables:**
- Railway will **automatically redeploy** your API
- Wait 2-3 minutes for deployment to complete

---

## 🌐 **PART 2: Vercel (Admin CMS Frontend)**

### **Where to Add:**
1. Go to: https://vercel.com/dashboard
2. Select your project: **first-in-dallas-cms** (your admin CMS)
3. Go to: **Settings** → **Environment Variables**
4. Click **"Add New"** for each variable

### **Variables to Add:**

#### **Variable 1: NEXT_PUBLIC_API_URL**
- **Key**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://wonderful-vibrancy-production.up.railway.app`
- **Environments**: ✅ Production, ✅ Preview, ✅ Development

#### **Variable 2: NEXT_PUBLIC_SUPABASE_URL**
- **Key**: `NEXT_PUBLIC_SUPABASE_URL`
- **Value**: `https://jwlvikkbcjrnzsvhyfgy.supabase.co`
- **Environments**: ✅ Production, ✅ Preview, ✅ Development

#### **Variable 3: NEXT_PUBLIC_SUPABASE_ANON_KEY**
- **Key**: `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **Value**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0NjM3NzIsImV4cCI6MjA3NzAzOTc3Mn0.mRluKwZ2B0qg0Z8YGYCx4QRFMP5WwxiTef_olGDEJS4`
- **Environments**: ✅ Production, ✅ Preview, ✅ Development

### **After Adding Variables:**
1. Go to: **Deployments** tab
2. Click **"..."** (three dots) on the latest deployment
3. Click **"Redeploy"**
4. Wait 1-2 minutes

---

## 🔄 **PART 3: Check if Worker is Running**

The Ticketmaster sync needs a **worker** to process the tasks. Check if you have a worker service on Railway:

### **Option A: Worker Service Exists**
If you see a "worker" service in Railway:
1. Click on it
2. Check **Variables** tab
3. Make sure it has the same variables as the API (especially `TICKETMASTER_API_KEY` and `REDIS_URL`)

### **Option B: No Worker Service**
If you don't have a worker service, you need to add it:

1. In Railway, click **"+ New"**
2. Select **"GitHub Repo"**
3. Choose your repo: **first-in-dallas-events**
4. **Custom Start Command**: `python worker/worker.py`
5. Add the same environment variables as the API

---

## 📊 **Summary - Quick Checklist**

### ☁️ Railway (API):
- [ ] `TICKETMASTER_API_KEY` = `Tx3dcKeerAsHFOrhBsO6JVK2HbT0AEoK`
- [ ] `TICKETMASTER_AFFILIATE_ID` = `6497023`
- [ ] `EVENTBRITE_API_TOKEN` = `MOZFNTBR4O22QQV33X2C`
- [ ] `SUPABASE_URL` = `https://jwlvikkbcjrnzsvhyfgy.supabase.co`
- [ ] `SUPABASE_SERVICE_ROLE_KEY` = (the long token)
- [ ] `DATABASE_URL` = (auto-configured)
- [ ] `REDIS_URL` = (check if exists)

### ☁️ Railway (Worker):
- [ ] Same variables as API above
- [ ] Service is running

### 🌐 Vercel (Admin CMS):
- [ ] `NEXT_PUBLIC_API_URL` = Railway API URL
- [ ] `NEXT_PUBLIC_SUPABASE_URL` = Supabase URL
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Supabase anon key
- [ ] Redeployed after adding variables

---

## 🧪 **Test the Setup**

### **1. Test Railway API:**
Open in browser: `https://wonderful-vibrancy-production.up.railway.app/docs`

You should see the FastAPI documentation with all endpoints including:
- `/api/sync/ticketmaster/dallas`
- `/api/ticketmaster/search`

### **2. Test Admin CMS:**
Open your Vercel URL, login, and go to Sync page.

Click **"Sync Ticketmaster Events"** - you should see:
- ✅ Task queued message
- ✅ Status updates
- ✅ Events appearing in your database within 2 minutes

---

## 🚨 **Why You're Not Seeing Events**

The sync failed because:
1. ❌ Railway doesn't have `TICKETMASTER_API_KEY` (or had the typo)
2. ❌ Worker might not be running to process the sync task
3. ❌ Vercel doesn't have API URL to connect to Railway

**Once you add these variables, it will work!**

---

## 📝 **After Setup:**

1. **Push the .env fix** (I fixed the typo):
   ```bash
   git add .env
   git commit -m "Fix Ticketmaster API key typo"
   git push
   ```

2. **Wait for Railway to redeploy** (automatic, 2-3 min)

3. **Test sync again** from your admin CMS

---

## 🎯 **Expected Results**

When working correctly:
- ✅ Click "Sync Ticketmaster Events"
- ✅ See message: "Ticketmaster bulk sync started"
- ✅ Task ID appears
- ✅ Within 1-2 minutes: 150-300 events imported
- ✅ Events visible in your Events page

---

**Need help?** Check Railway logs for errors:
1. Go to Railway → Your API service
2. Click **"Logs"** tab
3. Look for any errors related to Ticketmaster

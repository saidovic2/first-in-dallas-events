# 🚀 Production Deployment Guide

Complete step-by-step guide to deploy your Events CMS to production.

---

## 📋 **Deployment Architecture**

```
WordPress (Namecheap Shared Hosting)
    ↓ API calls
Events CMS (Railway - Free Cloud Hosting)
    ↓ stores data in
PostgreSQL Database (Railway - Included)
```

**Monthly Cost:** $2-5 (just WordPress hosting - Events CMS is FREE!)

---

## ✅ **Phase 1: Prepare Your Code for GitHub**

### **Step 1: Initialize Git Repository**

Open PowerShell in your project folder and run:

```powershell
# Initialize git (if not already done)
git init

# Check current status
git status
```

### **Step 2: Create Initial Commit**

```powershell
# Add all files (respects .gitignore)
git add .

# Create first commit
git commit -m "Initial commit - Events CMS ready for production"
```

### **Step 3: Verify No Sensitive Data**

```powershell
# Make sure .env is NOT tracked
git status

# Should NOT see .env in the list
```

✅ If `.env` appears, run: `git rm --cached .env`

---

## 🐙 **Phase 2: Push to GitHub**

### **Step 1: Create GitHub Account**

1. Go to https://github.com
2. Sign up (if you don't have an account)
3. Verify your email

### **Step 2: Create New Repository**

1. Click **"+"** in top right → **"New repository"**
2. **Repository name:** `events-cms` (or `first-in-dallas-events`)
3. **Description:** "Event management system for First in Dallas"
4. **Visibility:** Choose **Private** (recommended) or Public
5. **Do NOT initialize** with README (we already have code)
6. Click **"Create repository"**

### **Step 3: Connect Your Local Code to GitHub**

GitHub will show you commands. Use these:

```powershell
# Add GitHub as remote
git remote add origin https://github.com/YOUR-USERNAME/events-cms.git

# Push your code
git branch -M main
git push -u origin main
```

**Replace `YOUR-USERNAME` with your actual GitHub username!**

### **Step 4: Enter Credentials**

When prompted:
- **Username:** Your GitHub username
- **Password:** Create a **Personal Access Token**:
  1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token → Select "repo" scope → Generate
  3. Copy and paste as password

✅ **Your code is now on GitHub!**

---

## 🚂 **Phase 3: Deploy to Railway (FREE)**

Railway is perfect because:
- ✅ Free tier (generous limits)
- ✅ Supports Docker
- ✅ PostgreSQL included
- ✅ Auto-deploys from GitHub
- ✅ Easy setup (10 minutes)

### **Step 1: Sign Up for Railway**

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (easiest - connects automatically)
4. Authorize Railway to access your GitHub

### **Step 2: Create New Project**

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `events-cms`
4. Railway will detect your `docker-compose.yml`

### **Step 3: Add Services**

Railway needs to know about your services. You'll create 4 services:

#### **A. PostgreSQL Database**

1. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway creates it automatically
3. Copy the **Connection URL** (we'll need it later)

#### **B. Redis**

1. Click **"+ New"** → **"Database"** → **"Add Redis"**
2. Railway creates it automatically
3. Copy the **Connection URL**

#### **C. API Service**

1. Click **"+ New"** → **"GitHub Repo"** → Select your repo
2. **Root Directory:** Leave empty (uses root)
3. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 8000`
4. **Working Directory:** `api`
5. Click **"Deploy"**

Add **Environment Variables**:
- `DATABASE_URL` = (PostgreSQL connection URL from step A)
- `REDIS_URL` = (Redis connection URL from step B)
- `APIFY_API_TOKEN` = (your Apify token)
- `JWT_SECRET` = (generate random string)

#### **D. Worker Service**

1. Click **"+ New"** → **"GitHub Repo"** → Select your repo
2. **Working Directory:** `worker`
3. **Start Command:** `python worker.py`
4. Click **"Deploy"**

Add **Environment Variables** (same as API):
- `DATABASE_URL` = (PostgreSQL connection URL)
- `REDIS_URL` = (Redis connection URL)
- `APIFY_API_TOKEN` = (your Apify token)

### **Step 4: Get Your Production API URL**

1. Go to your **API service** in Railway
2. Click **"Settings"** → **"Networking"**
3. Click **"Generate Domain"**
4. Copy your URL (e.g., `https://events-cms-production.up.railway.app`)

✅ **Your Events CMS is now LIVE!**

---

## 🌐 **Phase 4: Deploy WordPress**

### **Step 1: Get Namecheap Shared Hosting**

1. Go to https://namecheap.com
2. Buy **Shared Hosting** (Stellar plan - $2.88/month)
3. Choose your domain name
4. Complete purchase

### **Step 2: Install WordPress on Namecheap**

1. Login to **cPanel**
2. Find **"WordPress"** installer
3. Click **"Install"**
4. Choose your domain
5. Set admin username/password
6. Click **"Install"**
7. Wait 5-10 minutes

### **Step 3: Upload Events CMS Plugin**

Option A: **Via FTP** (Recommended)
1. Open **FileZilla** or **cPanel File Manager**
2. Navigate to: `/public_html/wp-content/plugins/`
3. Upload your `events-cms-directory` folder
4. Done!

Option B: **Via WordPress Admin**
1. Create ZIP: `Compress-Archive -Path ".\wordpress-plugin\events-cms-directory" -DestinationPath ".\events-cms-directory.zip"`
2. WordPress Admin → Plugins → Add New → Upload
3. Upload ZIP and activate

### **Step 4: Configure Plugin with Production API**

1. Go to **Settings → Events CMS**
2. **Events CMS API URL:** `https://events-cms-production.up.railway.app/api`
   (Replace with YOUR Railway URL from Phase 3, Step 4)
3. Click **"Save Changes"**

### **Step 5: Create Events Page**

1. Pages → Add New
2. Title: **"Events"**
3. Content: `[events_directory]`
4. Click **"Publish"**

✅ **Your live website now shows events!**

---

## 🔐 **Phase 5: Security & Optimization**

### **Update CORS for Production**

Your API needs to allow your live domain. Update `api/main.py`:

```python
allow_origins=[
    "http://localhost:3000", 
    "http://localhost:3001",
    "http://first-in-dallas.local",
    "https://first-in-dallas.local",
    "https://yourdomain.com",  # Add your live domain
    "https://www.yourdomain.com"  # Add www version
],
```

Commit and push:
```powershell
git add .
git commit -m "Add production domain to CORS"
git push
```

Railway will auto-deploy the update!

### **Setup Database Backups**

Railway has automatic backups, but also:
1. Railway Dashboard → Database → Backups
2. Enable **Automatic Backups**
3. Download initial backup

### **Monitor Your Services**

1. Railway Dashboard → Your Project
2. Check all services are **"Active"**
3. View logs if any issues

---

## 📊 **Testing Production**

### **Test 1: API Health Check**

Visit: `https://your-railway-url.up.railway.app/health`

Should see: `{"status": "healthy"}`

### **Test 2: API Events Endpoint**

Visit: `https://your-railway-url.up.railway.app/api/events?limit=5`

Should see: JSON array of events

### **Test 3: WordPress Events Page**

Visit: `https://yourdomain.com/events`

Should see: Your events directory!

### **Test 4: Add New Event**

1. Go to your **local** Events CMS dashboard
2. Add a test event from Facebook/Eventbrite
3. Check if it appears on **live** WordPress

✅ If all tests pass - **YOU'RE LIVE!** 🎉

---

## 🔄 **Making Updates**

### **Workflow for Changes:**

```powershell
# 1. Make changes locally
# 2. Test locally

# 3. Commit changes
git add .
git commit -m "Description of changes"

# 4. Push to GitHub
git push

# 5. Railway auto-deploys!
# Wait 2-3 minutes for deployment
```

---

## 💰 **Cost Breakdown**

| Service | Cost | What It Does |
|---------|------|--------------|
| **WordPress Hosting** | $2-5/month | Your website |
| **Railway (Events CMS)** | FREE | Event management system |
| **PostgreSQL** | FREE (included) | Database |
| **Redis** | FREE (included) | Task queue |
| **Domain** | $10-15/year | yourdomain.com |

**Total Monthly Cost:** $2-5 💪

---

## 📝 **Production Checklist**

Before going live, verify:

- [ ] Code pushed to GitHub
- [ ] Railway services deployed (API + Worker)
- [ ] Database connected and working
- [ ] Redis connected
- [ ] Environment variables set
- [ ] WordPress installed on Namecheap
- [ ] Plugin uploaded and activated
- [ ] Production API URL configured
- [ ] Events page created
- [ ] CORS updated with live domain
- [ ] Test events showing correctly
- [ ] All links working (View Details buttons)
- [ ] Mobile responsive (test on phone)

---

## 🆘 **Troubleshooting**

### **Events not showing on live site**

1. Check API URL in WordPress settings
2. Verify Railway API service is running
3. Check CORS includes your domain
4. Test API directly: `https://your-api.railway.app/api/events`

### **Railway deployment failed**

1. Check Railway logs
2. Verify environment variables are set
3. Check `docker-compose.yml` syntax
4. Ensure database is connected

### **WordPress plugin error**

1. Deactivate and reactivate plugin
2. Check API URL is correct (include `/api`)
3. Clear WordPress cache
4. Check WordPress error logs

---

## 🎓 **Next Steps After Launch**

1. **Set up automatic syncs** - Schedule Eventbrite/Facebook syncs
2. **Monitor performance** - Check Railway metrics
3. **Add more sources** - ICS feeds, RSS, manual entry
4. **Customize design** - Match your brand
5. **SEO optimization** - Add meta descriptions
6. **Analytics** - Track event views
7. **Backup strategy** - Regular database exports

---

## 📞 **Support Resources**

- **Railway Docs:** https://docs.railway.app
- **Namecheap Support:** https://namecheap.com/support
- **WordPress Forums:** https://wordpress.org/support
- **Your Project Docs:** See README.md

---

**You're ready to go live! Follow this guide step-by-step and you'll have a production website in about 1 hour!** 🚀

**Start with Phase 1 now!**

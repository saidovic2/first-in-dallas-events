# Fix Frontend Build Error on Railway

## The Problem

Railway deployment failing with: **"Error creating build plan with Railpack"**

Railway is trying to auto-detect your build configuration but failing because it's looking at the root directory instead of the `web` folder.

---

## ✅ FIX NOW (5 minutes)

### Step 1: Configure Build Settings Manually

In Railway, for the **"Events CMS frontend"** service:

1. Click **"Settings"** tab
2. Scroll to **"Build"** section
3. You should see something like "Builder: RAILPACK" or similar

**Change these settings:**

#### Root Directory
```
web
```
⚠️ **CRITICAL:** This tells Railway to look in the `web` folder, not root!

#### Build Command
```
npm run build
```

#### Start Command  
```
npm run start
```

#### Install Command (if asked)
```
npm install
```

### Step 2: Disable Railpack (Use NPM Instead)

Look for **"Builder"** dropdown or toggle:
- If you see "RAILPACK", change to **"NPM"** or **"NIXPACKS"**
- OR look for "Use custom build settings" toggle and enable it

### Step 3: Environment Variables

Make sure these are set in **Variables** tab:

```
NODE_ENV = production
NEXT_PUBLIC_API_URL = <first-in-dallas-events domain>
NEXT_PUBLIC_SUPABASE_URL = https://jwlvikkbcjrnzsvhyfgy.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0NjM3NzIsImV4cCI6MjA3NzAzOTc3Mn0.mRluKwZ2B0qg0Z8YGYCx4QRFMP5WwxiTef_olGDEJS4
```

### Step 4: Networking/Port Configuration

**Settings → Networking:**

#### Port (if asked):
- **Leave empty** (Railway auto-detects)
- OR set to **3000** (but Railway will override it anyway)
- Next.js automatically uses Railway's `$PORT` variable

#### Public Networking:
- **Enable** (toggle on)
- Click **"Generate Domain"**

### Step 5: Redeploy

1. Go to **Deployments** tab
2. Click three dots on failed deployment
3. Click **"Redeploy"**
4. OR push a new commit to trigger deployment

---

## 📊 Correct Configuration Summary

| Setting | Value |
|---------|-------|
| **Root Directory** | `web` |
| **Builder** | NPM (not Railpack) |
| **Build Command** | `npm run build` |
| **Start Command** | `npm run start` |
| **Install Command** | `npm install` |
| **Port** | Leave empty or 3000 |
| **NODE_ENV** | `production` |

---

## 🐛 Troubleshooting

### Error: "Cannot find package.json"
**Fix:** Root Directory must be set to `web`

### Error: "Module not found"
**Fix:** 
- Check all dependencies in package.json
- Ensure `npm install` runs before build
- Check Install Command is set

### Error: "Build succeeded but app crashes"
**Fix:**
- Check NEXT_PUBLIC_API_URL is correct
- Verify API domain is accessible
- Check deployment logs for specific error

### Port Configuration Not Available
**Fix:**
- Railway auto-handles ports for Next.js
- You don't need to manually configure port
- If there's a "Port" field, leave it empty

---

## ✅ What Success Looks Like

After correct configuration:

1. ✅ Build process completes successfully
2. ✅ Deployment shows green checkmark
3. ✅ Public domain generated
4. ✅ Visiting domain shows login page
5. ✅ No errors in deployment logs

---

## 🎯 Port Information for Railway

### How Railway Handles Ports:

1. **Railway assigns dynamic port** via `PORT` environment variable
2. **Next.js automatically uses** this port when you run `next start`
3. **You don't configure port manually** in Railway settings
4. **Railway auto-detects** which port your app listens on

### Default Ports (FYI):
- Next.js dev: 3000
- Next.js production: Uses `$PORT` from Railway
- Railway assigns: Usually 8000-9000 range

**Bottom line: Ignore port configuration, Railway handles it!**

---

## 🚀 Quick Fix Checklist

Do these in order:

- [ ] Settings → Build → Set Root Directory to `web`
- [ ] Set Build Command to `npm run build`
- [ ] Set Start Command to `npm run start`
- [ ] Change Builder from Railpack to NPM
- [ ] Variables tab → Add 4 environment variables
- [ ] Settings → Networking → Enable + Generate Domain
- [ ] Deployments → Redeploy
- [ ] Wait 3-5 minutes for build
- [ ] Check deployment logs for success

---

## ⚠️ Most Important Setting

**Root Directory = `web`**

Without this, Railway looks at project root and can't find your Next.js app!

---

**After fixing, deployment should succeed and you'll have a working CMS!** 🎉

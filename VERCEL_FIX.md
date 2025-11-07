# Fix Vercel Build Error

## Problem
Vercel can't find `package.json` because your Next.js app is in the `hub/` subdirectory, not the root.

## Solution: Configure Root Directory in Vercel Dashboard

### Step 1: Go to Vercel Project Settings
1. Open your project on Vercel dashboard
2. Go to **Settings** → **General**

### Step 2: Set Root Directory
1. Scroll to **Root Directory** section
2. Click **Edit**
3. Enter: `hub`
4. Click **Save**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click **Redeploy** on the latest deployment
3. The build should now succeed!

---

## Alternative: Deploy from hub/ Directory Only

If you prefer to deploy only the CMS (hub folder):

### Option A: Using Vercel CLI

```bash
cd hub
vercel --prod
```

### Option B: Connect hub/ as a separate project

1. In Vercel dashboard, create a **new project**
2. Connect your GitHub repo
3. In project settings, set **Root Directory** to `hub`
4. Deploy

---

## For Your deploy-all.ps1 Script

Update your deployment script to deploy from the hub directory:

```powershell
# Deploy CMS to Vercel (from hub directory)
Push-Location hub
vercel --prod --yes
Pop-Location
```

---

## Current Vercel Configuration

Your `vercel.json` is now minimal. All configuration should be done in the Vercel dashboard:
- **Root Directory**: `hub`
- **Build Command**: `npm run build` (default)
- **Output Directory**: `.next` (default)
- **Install Command**: `npm install` (default)

After setting the root directory, everything else will work automatically!

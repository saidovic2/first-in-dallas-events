# Deploy Frontend to Railway (FREE Solution)

## The Problem

Vercel deployment failing: "No more than 12 Serverless Functions on Hobby plan"

Your CMS has too many routes/pages for Vercel's free plan.

---

## ✅ Solution: Deploy Frontend to Railway (FREE)

Railway offers more generous free tier. Let's deploy your CMS there.

---

## 🚀 Deploy to Railway (10 minutes)

### Step 1: Create New Service for Frontend

1. Go to **Railway Dashboard**
2. Click your project
3. Click **"+ New Service"**
4. Select **"GitHub Repo"**
5. Connect to your repository: `saidovic2/first-in-dallas-events`
6. Railway will create a new service

### Step 2: Configure Frontend Service

1. Click the new service (might be called "web" or auto-generated name)
2. Click **"Settings"** tab
3. Scroll to **"Build"** section

**Configure these settings:**

```
Root Directory: web
Build Command: npm run build
Start Command: npm run start
Install Command: npm install
```

### Step 3: Add Environment Variables

1. Still in the new service
2. Click **"Variables"** tab
3. Click **"+ New Variable"** and add:

```
NEXT_PUBLIC_API_URL = <Get from first-in-dallas-events Settings → Networking → Copy domain>
NEXT_PUBLIC_SUPABASE_URL = https://jwlvikkbcjrnzsvhyfgy.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0NjM3NzIsImV4cCI6MjA3NzAzOTc3Mn0.mRluKwZ2B0qg0Z8YGYCx4QRFMP5WwxiTef_olGDEJS4
NODE_ENV = production
```

### Step 4: Generate Domain for Frontend

1. Still in new service
2. **Settings** → **Networking**
3. Click **"Generate Domain"**
4. Copy the domain (e.g., `web-production-xyz.up.railway.app`)

### Step 5: Deploy

1. Go to **Deployments** tab
2. Service should auto-deploy
3. Wait 2-3 minutes
4. Check for green checkmark

### Step 6: Access Your CMS

Go to the domain from Step 4: `https://your-web-domain.up.railway.app`

Should see your CMS login page!

---

## ⚠️ Important: Get Correct API Domain First

Before adding `NEXT_PUBLIC_API_URL` variable:

1. Click **first-in-dallas-events** service
2. Go to **Settings** → **Networking**
3. **Generate Domain** if not exists
4. Copy the domain
5. Test it: `curl https://domain/health` (should return `{"status":"healthy"}`)
6. Then use this domain in frontend environment variable

---

## 📋 Checklist

- [ ] Create new Railway service for frontend
- [ ] Configure: Root Directory = `web`
- [ ] Configure: Build Command = `npm run build`
- [ ] Configure: Start Command = `npm run start`
- [ ] Add 4 environment variables
- [ ] Generate public domain
- [ ] Wait for deployment
- [ ] Test CMS login page
- [ ] Test sync functionality

---

## 🐛 Troubleshooting

### Build fails with "Cannot find module"

**Fix:**
- Check `web/package.json` exists
- Verify Root Directory = `web`

### Environment variables not working

**Fix:**
- Variables must start with `NEXT_PUBLIC_` for client-side access
- Redeploy after adding variables

### CMS loads but sync doesn't work

**Fix:**
- Verify `NEXT_PUBLIC_API_URL` points to first-in-dallas-events domain
- Test API domain works: `curl https://api-domain/health`

---

## 💰 Cost Comparison

| Platform | Free Tier | Your Status |
|----------|-----------|-------------|
| **Vercel** | 12 serverless functions | ❌ Exceeded |
| **Railway** | $5 free credit/month | ✅ Should work |

Railway is more suitable for this type of application!

---

## Alternative: Optimize for Vercel (Not Recommended)

If you really want to stay on Vercel, you'd need to:
1. Reduce number of pages
2. Combine API routes
3. Remove unused routes
4. OR upgrade to Vercel Pro ($20/month)

**But Railway is easier and free!**

---

## ✅ After Frontend Deploys to Railway

Your architecture will be:

```
Frontend (Railway) → API (Railway) → Worker (Railway)
                          ↓
                    PostgreSQL (Railway)
                          ↓
                    Redis (Railway)
```

All in one platform = easier to manage!

---

**Start with Step 1: Create new Railway service for web directory**

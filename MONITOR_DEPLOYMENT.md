# Monitor Your Frontend Deployment

## What to Watch For (Next 3-5 Minutes)

### Step 1: Check Deployment Status

**Railway → Events CMS frontend service → Deployments tab**

You should see:
1. ⏳ **"Building..."** → Building Docker image
2. ⏳ **"Deploying..."** → Starting the container
3. ✅ **"Active"** → Success! (green checkmark)

---

## ✅ Signs of Success

### In Deployment Logs:

Look for these messages:

```
✓ Building Docker image
✓ Installing dependencies (npm install)
✓ Building Next.js application (npm run build)
✓ Creating optimized production build
✓ Compiled successfully
✓ Starting server (npm run start)
✓ Ready on http://0.0.0.0:3000
```

---

## ❌ If Build Fails

### Common Errors:

#### Error: "Cannot find module"
```
Missing dependency in package.json
Fix: Check web/package.json has all required packages
```

#### Error: "NEXT_PUBLIC_API_URL is not defined"
```
Environment variable missing
Fix: Variables tab → Add NEXT_PUBLIC_API_URL
```

#### Error: "Build timed out"
```
Build taking too long (Railway limit)
Fix: Should work on retry - click "Redeploy"
```

#### Error: "Root directory not found"
```
Root Directory not set correctly
Fix: Settings → Root Directory = "web" (no slashes)
```

---

## ✅ After Successful Deployment

### 1. Get Your CMS URL

**Settings → Networking**
- Copy the domain (e.g., `events-cms-frontend-production.up.railway.app`)

### 2. Test the Frontend

Open in browser:
```
https://your-frontend-domain.up.railway.app
```

**Should see:**
- ✅ CMS Login page
- ✅ No errors in browser console

### 3. Test Login

1. Login with your credentials
2. Should redirect to dashboard
3. Check if dashboard loads

### 4. Test Sync Function

1. Go to **Sync** page
2. Click **"Sync Eventbrite Events"**
3. Should show success message or progress

**If sync fails:**
- Check `NEXT_PUBLIC_API_URL` points to correct API domain
- Test API: `curl https://api-domain/health`
- Check browser console for errors

---

## 🔍 Troubleshooting During Build

### Build is Taking Long Time (>5 minutes)

**Normal for first build:**
- Installing all npm packages
- Building Next.js
- Creating production bundle

**If stuck after 10 minutes:**
- Check deployment logs for errors
- May need to cancel and redeploy

### Build Fails at "npm install"

**Causes:**
- Network issues
- Railway timeout
- Missing package.json

**Fix:**
- Verify `web/package.json` exists
- Redeploy (may work on retry)

### Build Fails at "npm run build"

**Causes:**
- TypeScript errors
- Missing environment variables (NEXT_PUBLIC_*)
- Build configuration issues

**Fix:**
- Check all NEXT_PUBLIC_* variables set
- Check deployment logs for specific error

---

## 📊 Full Deployment Timeline

```
0:00 - Deployment triggered
0:01 - Pulling source code from GitHub
0:02 - Building Docker image
0:03 - Running npm install (1-2 minutes)
0:04 - Running npm run build (1-2 minutes)
0:05 - Starting container
0:06 - ✅ Service Active
```

**Total time: 3-6 minutes**

---

## ✅ Success Checklist

After deployment succeeds:

- [ ] Deployment shows green checkmark
- [ ] Public domain accessible
- [ ] Login page loads
- [ ] Can login successfully
- [ ] Dashboard loads
- [ ] Sync page accessible

---

## 🎯 Final Configuration Check

Before testing sync, verify:

### 1. API Service is Working

```powershell
curl "https://your-api-domain.up.railway.app/health"
```
Should return: `{"status":"healthy"}`

### 2. Frontend Has Correct API URL

**Railway → Frontend service → Variables tab**

Check `NEXT_PUBLIC_API_URL` matches your API domain

### 3. WordPress is Updated

**WordPress Admin → Settings → Events CMS**

API URL should be: `https://your-api-domain.up.railway.app/api`

### 4. Database Events are Published

**Railway → PostgreSQL → Query:**
```sql
SELECT status, COUNT(*) FROM events GROUP BY status;
```

Should show events with `PUBLISHED` status

---

## 🚀 What to Do After Success

1. **Test Sync:**
   - Login to CMS
   - Sync → Click "Sync Eventbrite Events"
   - Should fetch and save events

2. **Check Events:**
   - Go to Events page in CMS
   - Should see events listed

3. **Check WordPress:**
   - Visit WordPress Events page
   - Should see current events

4. **Update Bookmarks:**
   - Save new CMS URL
   - Update any links/bookmarks

---

## 📞 If Still Not Working After Deployment

**Check these in order:**

1. ✅ Frontend deployed successfully (green checkmark)
2. ✅ Frontend domain accessible (login page loads)
3. ✅ API service has public domain
4. ✅ API /health endpoint works
5. ✅ Frontend NEXT_PUBLIC_API_URL is correct
6. ✅ All environment variables set
7. ✅ Can login to CMS
8. ✅ Browser console shows no errors

**If sync still fails:**
- Check browser Network tab for failed requests
- Check API deployment logs
- Verify Worker service is running
- Check database connection

---

## 🎉 When Everything Works

You should be able to:

✅ Access CMS dashboard
✅ Sync events from Eventbrite
✅ View events in CMS
✅ Events appear on WordPress
✅ No errors in logs

---

**Right now:** Watch the Deployments tab for build progress!

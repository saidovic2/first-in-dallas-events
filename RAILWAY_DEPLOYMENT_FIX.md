# 🚂 Railway Deployment Fix Guide

## Issues Fixed

1. **Build plan errors with Nixpacks** - Created `railway.toml` files to force Docker builds
2. **Missing PORT configuration** - Updated Dockerfiles to use Railway's PORT variable
3. **Event sync not working** - Need to check database connection and environment variables

## 🔧 Steps to Fix Railway Deployment

### 1. Push the New Configuration Files

```powershell
# Stage the new files
git add api/railway.toml
git add worker/railway.toml
git add web/railway.toml
git add api/Dockerfile
git add worker/Dockerfile

# Commit
git commit -m "Fix Railway deployment configuration"

# Push to trigger redeployment
git push
```

### 2. Configure Railway Services

#### Service 1: API (first-in-dallas-events)

1. Go to Railway Dashboard → Select "first-in-dallas-events" service
2. **Settings → Environment Variables** - Add/verify:
   ```
   DATABASE_URL=<your-railway-postgres-url>
   REDIS_URL=<your-railway-redis-url>
   JWT_SECRET=<generate-random-secret>
   EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C
   TICKETMASTER_API_KEY=Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK
   TICKETMASTER_AFFILIATE_ID=6497023
   SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=<your-supabase-key>
   ```

3. **Settings → Build**
   - Build Command: (leave empty - uses Dockerfile)
   - Watch Paths: `api/**`

4. **Settings → Deploy**
   - Root Directory: `/api`
   - Dockerfile Path: `Dockerfile`

#### Service 2: Worker (wonderful-vibrancy)

1. Go to Railway Dashboard → Select "wonderful-vibrancy" service
2. **Settings → Environment Variables** - Add same as API
3. **Settings → Build**
   - Build Command: (leave empty - uses Dockerfile)
   - Watch Paths: `worker/**`

4. **Settings → Deploy**
   - Root Directory: `/worker`
   - Dockerfile Path: `Dockerfile`

### 3. Redeploy Services

After pushing the changes, Railway will automatically redeploy. Monitor:

1. **API Service Logs** - Should see:
   ```
   ✅ Database tables created/verified
   Database initialization complete!
   Application startup complete
   Uvicorn running on http://0.0.0.0:8000
   ```

2. **Worker Service Logs** - Should see:
   ```
   🟢 Worker started, waiting for tasks...
   Connected to Redis
   ```

### 4. Verify Deployment

Test your API:
```
https://your-api-domain.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

## 🐛 Common Issues & Solutions

### Issue: "Error creating build plan with Nixpacks"
**Solution:** The `railway.toml` files force Docker builds instead of Nixpacks.

### Issue: "Failed to build an image"
**Solution:** 
- Check Dockerfile syntax
- Verify root directory is set correctly in Railway
- Ensure requirements.txt exists in each service folder

### Issue: Port binding errors
**Solution:** Railway automatically sets PORT variable. Updated Dockerfiles use `${PORT:-8000}`

### Issue: Database connection failed
**Solution:**
- Verify DATABASE_URL is set in Railway environment variables
- Ensure PostgreSQL service is running
- Check database migrations ran successfully in logs

### Issue: Events not syncing
**Solution:**
1. Check Redis connection in both API and Worker
2. Verify EVENTBRITE_API_TOKEN is set
3. Check worker logs for errors
4. Test API endpoint: `/api/sync/eventbrite`

## 📊 Monitoring Your Services

### Check Service Health
```bash
# API Health
curl https://your-api.railway.app/health

# List Events
curl https://your-api.railway.app/api/events?limit=10
```

### View Logs in Real-Time
1. Railway Dashboard → Select Service
2. Click "View Logs"
3. Watch for errors during deployment

### Database Check
1. Railway Dashboard → PostgreSQL service
2. Click "Connect" → Copy connection string
3. Use pgAdmin or psql to inspect tables

## 🔄 Updating Your Deployment

For any code changes:

```powershell
# Make changes locally
# Test locally first

# Commit and push
git add .
git commit -m "Your change description"
git push

# Railway auto-deploys!
```

## 📝 Next Steps After Deployment

1. ✅ Verify API is accessible
2. ✅ Test Eventbrite sync
3. ✅ Check WordPress plugin connection
4. ✅ Sync some events
5. ✅ Verify events appear in WordPress

## 🆘 If Deployment Still Fails

1. **Check Railway Build Logs**
   - Look for specific error messages
   - Common issues: missing dependencies, syntax errors

2. **Verify File Structure**
   ```
   project-root/
   ├── api/
   │   ├── Dockerfile
   │   ├── railway.toml
   │   ├── requirements.txt
   │   └── ...
   ├── worker/
   │   ├── Dockerfile
   │   ├── railway.toml
   │   ├── requirements.txt
   │   └── ...
   └── web/
       ├── Dockerfile
       ├── railway.toml
       └── ...
   ```

3. **Contact Support**
   - Railway Discord: https://discord.gg/railway
   - Railway Docs: https://docs.railway.app

---

**You should now have working Railway deployments!** 🎉

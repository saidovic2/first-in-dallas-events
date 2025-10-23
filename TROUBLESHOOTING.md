# 🔧 Troubleshooting Guide

## Link Not Working? Follow These Steps

### Step 1: Check if Docker is Running

```powershell
# Check Docker status
docker --version
docker ps
```

**Expected Output**: Should show Docker version and running containers

**If Docker is not running**:
- Open Docker Desktop
- Wait for it to fully start (green icon in system tray)
- Try again

---

### Step 2: Check if Services are Running

```powershell
# Check all services
docker-compose ps
```

**Expected Output**: All services should show "Up" status
```
NAME            STATUS
events_api      Up
events_db       Up (healthy)
events_redis    Up (healthy)
events_web      Up
events_worker   Up
```

**If services are not running**:
```powershell
# Start services
docker-compose up -d
```

---

### Step 3: Check Service Logs

```powershell
# Check web frontend logs
docker-compose logs web

# Check API logs
docker-compose logs api

# Check all logs
docker-compose logs
```

**Look for errors** like:
- Port already in use
- Module not found
- Connection refused
- Build errors

---

### Step 4: Common Issues & Solutions

#### Issue 1: "Port 3000 already in use"

**Solution A**: Stop other services using port 3000
```powershell
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Solution B**: Change the port in docker-compose.yml
```yaml
web:
  ports:
    - "3001:3000"  # Change 3000 to 3001
```

Then access at: http://localhost:3001

---

#### Issue 2: "Cannot GET /" or Blank Page

**Cause**: Frontend not built or crashed

**Solution**:
```powershell
# Rebuild web container
docker-compose up -d --build web

# Check logs for errors
docker-compose logs -f web
```

**Wait 2-3 minutes** for Next.js to compile

---

#### Issue 3: "API Connection Failed" or "Network Error"

**Cause**: Backend not running or wrong URL

**Solution**:
```powershell
# Check if API is running
docker-compose ps api

# Test API directly
curl http://localhost:8000/health
# Or open in browser: http://localhost:8000/health

# Restart API
docker-compose restart api

# Check API logs
docker-compose logs -f api
```

---

#### Issue 4: "Database Connection Error"

**Cause**: PostgreSQL not ready

**Solution**:
```powershell
# Check database status
docker-compose ps db

# Restart database
docker-compose restart db

# Wait 10 seconds, then restart API
Start-Sleep -Seconds 10
docker-compose restart api
```

---

#### Issue 5: "Module not found" Errors

**Cause**: Dependencies not installed

**Solution**:
```powershell
# Rebuild all containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

This will take 5-10 minutes but ensures clean build.

---

### Step 5: Complete Reset (Nuclear Option)

If nothing works, do a complete reset:

```powershell
# Stop and remove everything
docker-compose down -v

# Remove all containers and volumes
docker system prune -a --volumes

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d

# Wait 3-5 minutes for everything to start
```

---

### Step 6: Verify Each Service

#### Test Database
```powershell
docker-compose exec db psql -U postgres -d events_cms -c "SELECT COUNT(*) FROM events;"
```
Should show event count (6 if seed data loaded)

#### Test Redis
```powershell
docker-compose exec redis redis-cli ping
```
Should return: `PONG`

#### Test API
Open browser: http://localhost:8000/docs
Should show Swagger API documentation

#### Test Frontend
Open browser: http://localhost:3000
Should show login page or redirect

---

### Step 7: Check Specific URLs

Try accessing these URLs one by one:

1. **API Health**: http://localhost:8000/health
   - Should return: `{"status":"healthy"}`

2. **API Docs**: http://localhost:8000/docs
   - Should show Swagger UI

3. **Frontend**: http://localhost:3000
   - Should show login page

4. **Dashboard**: http://localhost:3000/dashboard
   - Should redirect to login if not authenticated

---

## 🐛 Debugging Commands

### View Real-time Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f api
docker-compose logs -f worker
```

### Check Container Status
```powershell
docker-compose ps
```

### Restart Specific Service
```powershell
docker-compose restart web
docker-compose restart api
docker-compose restart worker
```

### Access Container Shell
```powershell
# API container
docker-compose exec api sh

# Web container
docker-compose exec web sh

# Database container
docker-compose exec db psql -U postgres events_cms
```

### Check Network Connectivity
```powershell
# From web container to API
docker-compose exec web curl http://api:8000/health

# From API to database
docker-compose exec api python -c "import psycopg2; print('DB OK')"
```

---

## 📊 Expected Behavior

### After Running `setup.ps1`:

1. **Minute 0-1**: Building containers
2. **Minute 1-2**: Starting database and Redis
3. **Minute 2-3**: Starting API and worker
4. **Minute 3-4**: Starting web frontend
5. **Minute 4-5**: Next.js compilation

### When Everything is Working:

```powershell
docker-compose ps
```

Should show:
```
NAME            STATUS          PORTS
events_api      Up              0.0.0.0:8000->8000/tcp
events_db       Up (healthy)    0.0.0.0:5432->5432/tcp
events_redis    Up (healthy)    0.0.0.0:6379->6379/tcp
events_web      Up              0.0.0.0:3000->3000/tcp
events_worker   Up
```

### Browser Access:
- http://localhost:3000 → Login page
- http://localhost:8000 → API root
- http://localhost:8000/docs → API documentation

---

## 🚨 Error Messages & Solutions

### "Error: connect ECONNREFUSED 127.0.0.1:8000"
**Cause**: API not running or not accessible
**Solution**: 
```powershell
docker-compose restart api
docker-compose logs -f api
```

### "Error: Cannot find module 'next'"
**Cause**: npm packages not installed
**Solution**:
```powershell
docker-compose exec web npm install
docker-compose restart web
```

### "Error: relation 'events' does not exist"
**Cause**: Database not initialized
**Solution**:
```powershell
docker-compose exec api python init_db.py
```

### "Error: EADDRINUSE: address already in use"
**Cause**: Port already in use
**Solution**: See "Port already in use" section above

### "Error: Failed to connect to database"
**Cause**: Database not ready
**Solution**:
```powershell
docker-compose restart db
Start-Sleep -Seconds 10
docker-compose restart api
```

---

## 💡 Quick Fixes

### Quick Fix 1: Restart Everything
```powershell
docker-compose restart
```

### Quick Fix 2: Rebuild Web Only
```powershell
docker-compose up -d --build web
```

### Quick Fix 3: Check if Ports are Free
```powershell
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432
netstat -ano | findstr :6379
```

### Quick Fix 4: Fresh Start
```powershell
docker-compose down
docker-compose up -d
```

---

## 📞 Still Not Working?

### Collect Information:

1. **Docker version**:
   ```powershell
   docker --version
   docker-compose --version
   ```

2. **Service status**:
   ```powershell
   docker-compose ps
   ```

3. **Recent logs**:
   ```powershell
   docker-compose logs --tail=50
   ```

4. **Port usage**:
   ```powershell
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   ```

5. **System info**:
   ```powershell
   systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
   ```

### Manual Service Start (Alternative)

If Docker is causing issues, you can run services manually:

#### Start Database
```powershell
# Install PostgreSQL locally
# Create database: events_cms
# Update .env with local connection string
```

#### Start API
```powershell
cd api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

#### Start Worker
```powershell
cd worker
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python worker.py
```

#### Start Web
```powershell
cd web
npm install
npm run dev
```

---

## ✅ Success Checklist

- [ ] Docker Desktop is running
- [ ] All containers show "Up" status
- [ ] http://localhost:8000/health returns `{"status":"healthy"}`
- [ ] http://localhost:8000/docs shows Swagger UI
- [ ] http://localhost:3000 shows login page
- [ ] Can login with admin@example.com / admin123
- [ ] Dashboard shows statistics
- [ ] No errors in logs

---

## 🎯 Most Common Solution

**90% of issues are solved by**:

```powershell
# Stop everything
docker-compose down

# Start fresh
docker-compose up -d

# Wait 3 minutes
Start-Sleep -Seconds 180

# Check status
docker-compose ps

# Open browser
start http://localhost:3000
```

---

**Need more help? Check the logs first!**
```powershell
docker-compose logs -f
```

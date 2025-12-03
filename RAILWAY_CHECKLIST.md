# Railway Services Fix Checklist

Your services are deployed (green checkmarks) but not working. Follow this checklist:

---

## 1. Check Service Logs for Errors

### For first-in-dallas-events:
1. Railway Dashboard → Click **first-in-dallas-events**
2. Click **Deployments** tab
3. Click the latest deployment
4. **Scroll through the logs** - look for red errors

### Common Error Messages:

| Error Message | Solution |
|---------------|----------|
| `DATABASE_URL is not set` | Add DATABASE_URL variable (see step 3) |
| `REDIS_URL is not set` | Add REDIS_URL variable (see step 3) |
| `Connection to database failed` | Wrong DATABASE_URL or database not running |
| `Port already in use` | Already fixed in code - shouldn't happen |

---

## 2. Generate Public Domain

### For first-in-dallas-events (API):
1. Click **first-in-dallas-events** service
2. Go to **Settings** tab
3. Find **"Networking"** section
4. Look for **"Public Networking"** or **"Domains"**
5. You should see either:
   - A domain already listed (e.g., `first-in-dallas-events-production.up.railway.app`)
   - OR a button: **"Generate Domain"**
6. If no domain, click **"Generate Domain"**
7. **Copy the full domain URL**

**Example domains Railway generates:**
- `first-in-dallas-events-production.up.railway.app`
- `web-production-abc123.up.railway.app`
- Something similar

### For wonderful-vibrancy (Worker):
- Worker doesn't need a public domain
- Skip this step for worker

---

## 3. Add Environment Variables

### Critical Variables Needed:

Both **first-in-dallas-events** AND **wonderful-vibrancy** need these:

```bash
DATABASE_URL=<from PostgreSQL service>
REDIS_URL=<from Redis service>
JWT_SECRET=my-secret-key-change-this
EVENTBRITE_API_TOKEN=MOZFNTBR4O22QQV33X2C
TICKETMASTER_API_KEY=Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK
TICKETMASTER_AFFILIATE_ID=6497023
SUPABASE_URL=https://jwlvikkbcjrnzsvhyfgy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTQ2Mzc3MiwiZXhwIjoyMDc3MDM5NzcyfQ.hw6S9WncejbjqQG13hR3AYtFbldw3H5miuLQHpy6NIY
```

### How to Add Variables:

#### Step A: Get DATABASE_URL
1. In your Railway project, click **Postgres** service
2. Click **Variables** tab OR **Connect** tab
3. Look for **"DATABASE_URL"** or **"Connection String"**
4. **Copy the entire connection string**
   - Should look like: `postgresql://user:password@host:5432/database`

#### Step B: Get REDIS_URL
1. Click **Redis** service
2. Click **Variables** tab
3. Look for **"REDIS_URL"**
4. **Copy the entire connection string**
   - Should look like: `redis://default:password@host:6379`

#### Step C: Add Variables to API Service
1. Click **first-in-dallas-events** service
2. Click **Variables** tab
3. Click **"+ New Variable"** button
4. Add each variable:
   - Variable name: `DATABASE_URL`
   - Value: paste from Step A
   - Click "Add"
5. Repeat for each variable above

#### Step D: Add Variables to Worker Service
1. Click **wonderful-vibrancy** service
2. Click **Variables** tab
3. Add the **SAME variables** as Step C

**IMPORTANT:** Both services need the SAME environment variables!

---

## 4. Wait for Services to Redeploy

After adding variables:
- Services will automatically redeploy
- Wait 1-2 minutes
- Watch for green checkmarks
- If red X appears, check deployment logs for errors

---

## 5. Test API is Working

### In PowerShell:
```powershell
# Replace YOUR-DOMAIN with actual Railway domain from step 2
curl "https://YOUR-DOMAIN.up.railway.app/health"
```

**Expected response:**
```json
{"status":"healthy"}
```

**If you get 404 or error:**
- Domain not generated (go back to step 2)
- Service crashed (check deployment logs)
- Environment variables wrong (check step 3)

### Test events endpoint:
```powershell
curl "https://YOUR-DOMAIN.up.railway.app/api/events?limit=5"
```

**Expected:** JSON array (even if empty)

---

## 6. Update WordPress

Once API is working:

1. Login to **WordPress Admin**
2. Go to **Settings → Events CMS**
3. Find **"Events CMS API URL"** field
4. Enter: `https://YOUR-DOMAIN.up.railway.app/api`
   - **IMPORTANT:** Must end with `/api`
5. Click **"Save Changes"**

---

## 7. Fix Database Events Status

Your events exist but have `DRAFT` status. WordPress requests `PUBLISHED` events.

### In Railway:
1. Click **Postgres** service
2. Click **Query** tab
3. Paste this SQL:

```sql
-- Update all DRAFT events to PUBLISHED
UPDATE events 
SET status = 'PUBLISHED'
WHERE status = 'DRAFT';

-- Verify the update
SELECT status, COUNT(*) 
FROM events 
GROUP BY status;
```

4. Click **"Execute"** or **"Run"**

---

## 8. Test Everything

### Test 1: CMS Dashboard Sync
1. Go to your CMS dashboard: `https://your-cms.vercel.app`
2. Navigate to **Sync** page
3. Click **"Sync Eventbrite Events"**
4. Should show success message
5. Navigate to **Events** page
6. Should see events listed

### Test 2: WordPress Events Directory
1. Visit your WordPress site
2. Go to Events page
3. Should see current events
4. Old events (before today) filtered out

---

## Troubleshooting

### Problem: "Sync button shows error"

**Causes:**
1. CMS can't reach Railway API
2. API URL in CMS environment variables is wrong
3. CORS issue (already fixed in code)

**Fix:**
- Make sure Railway API has public domain
- Check CMS environment variable `NEXT_PUBLIC_API_URL`

### Problem: "CMS Directory is empty"

**Causes:**
1. No events in database
2. Events are DRAFT status (need PUBLISHED)
3. WordPress has wrong API URL

**Fix:**
- Update database events to PUBLISHED (step 7)
- Update WordPress API URL (step 6)
- Try syncing from Eventbrite

### Problem: "WordPress shows old events"

**Causes:**
1. WordPress using cached API URL
2. WordPress not updated with new Railway domain

**Fix:**
- Clear WordPress cache (if using caching plugin)
- Verify API URL in WordPress settings ends with `/api`
- Deactivate and reactivate Events CMS plugin

---

## Final Checklist

- [ ] first-in-dallas-events shows green checkmark
- [ ] wonderful-vibrancy shows green checkmark
- [ ] Postgres shows green checkmark
- [ ] Redis shows green checkmark
- [ ] first-in-dallas-events has public domain
- [ ] first-in-dallas-events has 8 environment variables
- [ ] wonderful-vibrancy has 8 environment variables
- [ ] API /health returns {"status":"healthy"}
- [ ] WordPress has correct API URL
- [ ] Database events are PUBLISHED status
- [ ] CMS sync button works
- [ ] WordPress shows current events

---

## Most Common Issue

**Missing DATABASE_URL and REDIS_URL variables!**

Without these, the API service can't connect to database and will crash or not respond properly.

Go to Railway → first-in-dallas-events → Variables tab → Add DATABASE_URL and REDIS_URL

---

**After completing ALL steps above, your CMS will work!**

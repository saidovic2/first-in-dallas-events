# 🤖 Automated Event Sync & Publish System

## Overview

Your Events CMS now runs **fully automated** with no manual intervention needed!

### ✅ What Happens Automatically:

1. **📥 Event Syncing** - Pulls fresh events from all sources 2x daily
2. **📤 Auto-Publishing** - New events automatically publish to WordPress
3. **🧹 Cleanup** - Old events (30+ days past) auto-deleted daily

---

## 📅 Schedule

### Daily Syncs (2x per day)
- **Morning Sync:** 8:00 AM Central Time
- **Evening Sync:** 6:00 PM Central Time

### Daily Maintenance
- **Cleanup:** 2:00 AM Central Time (removes events >30 days old)

---

## 📊 Event Sources Synced Automatically

1. **Eventbrite Dallas** - Large-scale events across Dallas
2. **Dallas Arboretum** - Family & nature events
3. **Klyde Warren Park** - Park activities & festivals
4. **Perot Museum** - Science & education events
5. **Dallas Public Library** - Educational & community events
6. **Dallas Zoo** - Animal experiences & special events
7. **Fair Park** - Festivals & major events
8. **House of Blues Dallas** - Live music & concerts
9. **Factory Deep Ellum** - Music venue events

---

## 🔄 Auto-Sync Workflow

### Step 1: Event Collection (8 AM & 6 PM)
```
1. Scheduler triggers at scheduled time
2. Each source queued in Redis
3. Worker processes each source
4. New events saved as DRAFT
```

### Step 2: Auto-Publish (5 mins after sync)
```
1. Find all DRAFT events without WP post ID
2. Publish up to 50 events to WordPress
3. Update status to PUBLISHED
4. Store WordPress post ID
```

### Step 3: Daily Cleanup (2 AM)
```
1. Find events >30 days old
2. Delete from database
3. Log cleanup count
```

---

## 🎛️ Manual Controls

### Trigger Sync Manually (for testing)

**API Endpoint:**
```bash
POST /api/scheduler/trigger
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "message": "Manual sync triggered",
  "status": "running",
  "note": "Check logs for progress"
}
```

### Check Scheduler Status

**API Endpoint:**
```bash
GET /api/scheduler/status
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "scheduler_running": true,
  "job_count": 3,
  "jobs": [
    {
      "id": "morning_sync",
      "name": "Morning Event Sync (8 AM CT)",
      "next_run": "2025-12-04T08:00:00-06:00",
      "trigger": "cron[hour='8', minute='0']"
    },
    {
      "id": "evening_sync",
      "name": "Evening Event Sync (6 PM CT)",
      "next_run": "2025-12-03T18:00:00-06:00",
      "trigger": "cron[hour='18', minute='0']"
    },
    {
      "id": "daily_cleanup",
      "name": "Daily Event Cleanup (2 AM CT)",
      "next_run": "2025-12-04T02:00:00-06:00",
      "trigger": "cron[hour='2', minute='0']"
    }
  ]
}
```

---

## 📝 Logs

Check Railway logs to see sync progress:

```
================================================================================
🔄 STARTING AUTOMATED SYNC FOR ALL SOURCES
⏰ Time: 2025-12-03 08:00 AM
================================================================================
✓ Queued sync task for Eventbrite Dallas (ID: 1234)
✓ Queued sync task for Dallas Arboretum (ID: 1235)
✓ Queued sync task for Klyde Warren Park (ID: 1236)
...
✓ Queued 9 sync tasks

================================================================================
📤 AUTO-PUBLISHING NEW EVENTS TO WORDPRESS
================================================================================
📋 Found 42 new events to publish
  ✓ Published: ELENA ROSE - Alma US Tour 2025 (WP ID: 5678)
  ✓ Published: Dallas Mavericks vs Brooklyn Nets (WP ID: 5679)
  ...

📊 PUBLISH SUMMARY
  ✓ Published: 42
  ✗ Failed: 0
================================================================================
```

---

## ⚙️ Configuration

### Update Sync Schedule

Edit `api/scheduler.py`:

```python
# Morning sync: 8 AM Central Time
scheduler.add_job(
    sync_all_sources,
    CronTrigger(hour=8, minute=0, timezone='America/Chicago'),
    id='morning_sync'
)

# Evening sync: 6 PM Central Time  
scheduler.add_job(
    sync_all_sources,
    CronTrigger(hour=18, minute=0, timezone='America/Chicago'),
    id='evening_sync'
)
```

### Change Number of Auto-Publishes

Edit `api/scheduler.py`:

```python
# Publish max 50 at a time (line 107)
).limit(50).all()  # Change to 100, 200, etc.
```

### Adjust Cleanup Age

Edit `api/scheduler.py`:

```python
# Delete events older than 30 days (line 162)
cutoff_date = datetime.now() - timedelta(days=30)  # Change to 60, 90, etc.
```

---

## 🚨 Troubleshooting

### Scheduler Not Running

**Check Railway Logs:**
```
✅ Database tables created/verified
✅ Automated scheduler started (2x daily syncs)
```

If you see:
```
⚠️ Scheduler not started: ...
```

Check that `APScheduler==3.10.4` is in `requirements.txt`.

### Events Not Publishing

1. **Check WordPress credentials** in Railway environment variables:
   - `WP_BASE_URL`
   - `WP_USER`
   - `WP_APP_PASSWORD`

2. **Check logs** for publish errors:
   ```
   ✗ Failed: Event Title
   ```

### Manual Trigger Not Working

Make sure you're authenticated:
```bash
curl -X POST https://your-api.up.railway.app/api/scheduler/trigger \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Benefits

✅ **No Manual Work** - Set it and forget it  
✅ **Always Fresh** - Events update 2x daily  
✅ **Auto-Publishing** - New events go live automatically  
✅ **Clean Database** - Old events auto-deleted  
✅ **Reliable** - Runs in background on Railway  
✅ **Scalable** - Easy to add more sources  

---

## 📈 Next Steps

### Add Ticketmaster Auto-Sync

Currently, Ticketmaster uses Apify manual import. To automate:

1. Set up Apify actor to run on schedule
2. Use Apify webhooks to trigger import
3. Or add Apify API polling to scheduler

### Add More Sources

Edit `api/scheduler.py`:

```python
EVENT_SOURCES = [
    # ... existing sources ...
    {
        "name": "New Venue", 
        "type": "new_venue", 
        "url": "https://newvenue.com/events"
    },
]
```

---

## 🎉 You're All Set!

Your Events CMS now runs on autopilot. Check back occasionally to ensure everything's running smoothly, but no daily management needed!

**Questions?** Check Railway logs or API docs at `/docs`.

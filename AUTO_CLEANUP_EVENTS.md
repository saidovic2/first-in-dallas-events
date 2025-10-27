# 🗑️ Auto-Cleanup Past Events

## ✅ What Was Implemented:

### 1. **Auto-Filter Past Events** (API)
- Events API now **automatically hides past events** from the public directory
- Only shows **upcoming events** (events that haven't started yet)
- Admin can see past events by adding `?include_past=true` parameter

### 2. **Order Events by Date** (API)
- Events are now **ordered by start date (ascending)**
- **Closest/upcoming events show first** at the top
- Past events at the bottom (if included)

### 3. **Manual Cleanup Button** (CMS)
- **"Delete Past Events"** button in the Manage Events page
- Deletes events older than 7 days after their start date
- Shows confirmation dialog before deletion
- Displays count of deleted events

---

## 🚀 How It Works:

### **Public Directory (Automatic):**
```
GET /api/events/
```
- ✅ Only shows upcoming events
- ✅ Ordered by date (closest first)
- ✅ Past events automatically hidden

### **Admin View (Include Past):**
```
GET /api/events/?include_past=true
```
- Shows ALL events including past ones
- Still ordered by date

### **Manual Cleanup (Admin):**
1. Go to **Manage Events** page in CMS
2. Click **"Delete Past Events"** button (top right)
3. Confirm deletion
4. Events older than 7 days are permanently deleted

---

## 📅 Cleanup Schedule:

### **Option 1: Manual** (Current)
- Click the button whenever you want to clean up

### **Option 2: Automated (Recommended)**
Set up a cron job or Railway scheduled task:

```bash
# Run cleanup every day at 2 AM
curl -X POST https://your-api-url.com/api/events/cleanup/past-events?days_old=7 \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### **Railway Scheduled Task:**
1. Go to Railway Dashboard
2. Click your API service
3. Go to **Settings** → **Cron Jobs**
4. Add: `0 2 * * *` (daily at 2 AM)
5. Command: `curl -X POST http://localhost:8000/api/events/cleanup/past-events?days_old=7`

---

## 🎯 Benefits:

✅ **Public directory stays clean** - Only shows upcoming events
✅ **Better UX** - Users see relevant events first
✅ **Database performance** - Less old data to query
✅ **Manual control** - Delete past events when needed

---

## 🔧 Customization:

Change how many days before deletion:
```
?days_old=14  // Delete events older than 14 days
?days_old=30  // Delete events older than 30 days
```

**Current Setting:** 7 days after event start date

---

## ✅ Deploy:

1. **Commit changes:**
```bash
git add .
git commit -m "Add auto-cleanup for past events and date ordering"
git push
```

2. **Railway will auto-deploy** (1-2 minutes)

3. **Test:**
   - Public directory shows only upcoming events
   - CMS "Delete Past Events" button works

---

**Your events are now automatically organized and cleaned up!** 🎉

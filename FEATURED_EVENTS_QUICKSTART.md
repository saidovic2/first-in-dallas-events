# 🚀 Featured Events - Quick Start Guide

Get your featured events monetization system up and running in 10 minutes!

---

## ✅ **Prerequisites**

- ✅ Events CMS API running
- ✅ WordPress site with Events CMS Directory plugin
- ✅ Database access
- ✅ Python 3.7+ installed

---

## 📋 **5-Step Setup**

### **Step 1: Run Database Migration** (2 minutes)

```bash
cd "c:\Users\HP\Desktop\FiD- Events CMS"
python run_featured_migration.py
```

✅ **Expected Output:**
```
🚀 Running Featured Events Migration...
✅ Migration completed successfully!

💰 Pricing Tiers:
  PLATINUM   (Position 1): $149.00/week
  GOLD       (Position 2): $99.00/week
  SILVER     (Position 3): $69.00/week
  BRONZE     (Position 4): $49.00/week
```

---

### **Step 2: Restart API** (1 minute)

```bash
# Test the new endpoints
# Visit: http://localhost:8001/docs
# Look for "Featured Events" section
```

Or restart your API server:
```bash
docker-compose restart api
# OR
cd api && python main.py
```

---

### **Step 3: Deploy WordPress Plugin** (2 minutes)

```bash
.\upload-php-only.ps1
```

Then in WordPress Admin:
1. Go to **Plugins**
2. **Deactivate** "Events CMS Directory"
3. **Reactivate** "Events CMS Directory"
4. Clear your browser cache (Ctrl+Shift+Delete)

---

### **Step 4: Test Featured Section** (2 minutes)

Visit your events calendar page. You should see:
- ✨ "Featured Events" section at the top (when slots are active)
- 📋 Regular events list below

**Note**: No featured events will show until you create your first featured slot!

---

### **Step 5: Create Your First Featured Slot** (3 minutes)

#### **Option A: Using API Docs** (Easiest)

1. Visit: `http://localhost:8001/docs`
2. Login to get auth token
3. Find `POST /api/featured`
4. Click "Try it out"
5. Use this example:

```json
{
  "event_id": 123,
  "slot_position": 1,
  "tier": "PLATINUM",
  "price_paid": 149.00,
  "payment_frequency": "WEEKLY",
  "starts_at": "2025-11-20T00:00:00Z",
  "ends_at": "2025-11-27T23:59:59Z",
  "payment_status": "PAID",
  "payment_method": "MANUAL",
  "notes": "Test featured slot"
}
```

6. Click "Execute"
7. Refresh your calendar page!

#### **Option B: Using cURL**

```bash
# Replace YOUR_TOKEN and event_id with real values
curl -X POST "http://localhost:8001/api/featured" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 123,
    "slot_position": 1,
    "tier": "PLATINUM",
    "price_paid": 149.00,
    "payment_frequency": "WEEKLY",
    "starts_at": "2025-11-20T00:00:00Z",
    "ends_at": "2025-11-27T23:59:59Z",
    "payment_status": "PAID",
    "payment_method": "MANUAL",
    "notes": "Test featured slot"
  }'
```

---

## 🎨 **Visual Guide**

### **What You'll See**

1. **Featured Section** (top of calendar)
   - Purple gradient background
   - "✨ Featured Events" heading
   - 4 premium cards (if all slots filled)

2. **Featured Cards**
   - Tier badge (Platinum/Gold/Silver/Bronze)
   - Colored borders matching tier
   - Event image, title, date, venue
   - "View Details & Get Tickets" button

3. **Regular Events** (below featured section)
   - Standard grid layout
   - All other published events

---

## 🔍 **Verification Checklist**

- [ ] Database tables created (`featured_slots`, `featured_pricing`)
- [ ] API endpoints responding (`/api/featured/pricing`, `/api/featured/active`)
- [ ] WordPress plugin updated to v1.2.0
- [ ] Featured section appears on calendar (when slots exist)
- [ ] Test featured slot displays correctly
- [ ] Mobile responsive (check on phone)

---

## 🐛 **Troubleshooting**

### **Migration Failed**

```bash
# Check your database connection
python -c "from api.config import settings; print(settings.DATABASE_URL)"

# Make sure your API server is not running during migration
# Stop it, run migration, then restart
```

### **Featured Section Not Showing**

1. **Check API response:**
   ```bash
   curl http://localhost:8001/api/featured/active
   ```
   Should return an array (empty `[]` if no slots, or array of featured events)

2. **Check WordPress plugin version:**
   Go to Plugins → should show "Events CMS Directory" version **1.2.0**

3. **Clear all caches:**
   - WordPress cache
   - Browser cache (Ctrl+Shift+Delete)
   - Hard refresh (Ctrl+F5)

### **No Events in Featured Slot**

Make sure your test event:
- ✅ Has `status = "PUBLISHED"`
- ✅ Has `start_at` date in the future
- ✅ Exists in the database
- ✅ Has a valid `id` that you're using in the featured slot

---

## 💰 **Start Making Money**

### **1. Create Marketing Materials**

Create a "Feature Your Event" page with:
- Pricing table
- Benefits of featuring
- Contact form
- Examples of featured events

### **2. Reach Out to Organizers**

Email template:
```
Subject: Get 10x More Visibility - Feature Your Event!

Hi [Name],

We're excited to announce premium featured slots on First in Dallas!

Your event can now appear at the TOP of our calendar with:
✨ Premium positioning
🎨 Eye-catching design
📱 Mobile-optimized display
📈 10x more visibility

Pricing starts at just $49/week!

Interested? Reply to this email or call us at [phone].

Best,
First in Dallas Team
```

### **3. Track Performance**

Monitor:
- Featured slot occupancy rate
- Revenue per slot/month
- Organizer satisfaction
- Click-through rates

---

## 📊 **Revenue Goals**

**Year 1 Goals:**
- **Q1**: 25% occupancy → ~$2,400/quarter
- **Q2**: 50% occupancy → ~$4,800/quarter
- **Q3**: 75% occupancy → ~$7,200/quarter
- **Q4**: 100% occupancy → ~$9,600/quarter

**Total Year 1**: **~$24,000**

---

## 📚 **Additional Resources**

- **Full Documentation**: See `FEATURED_EVENTS_GUIDE.md`
- **API Reference**: http://localhost:8001/docs
- **Support**: support@firstindallas.com

---

## 🎉 **You're All Set!**

Your featured events system is now live! 

**Next steps:**
1. ✅ Test with a few events
2. 📝 Create marketing materials
3. 📧 Email your organizer list
4. 💰 Start accepting bookings!

**Questions?** Check the full guide or reach out for support.

---

**Happy monetizing!** 💎

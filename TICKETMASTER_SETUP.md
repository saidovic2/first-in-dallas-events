# 🎫 Ticketmaster Integration Setup

Your Ticketmaster integration is ready! This guide will help you configure and test it.

---

## 📋 **What You Need:**

- ✅ **API Key (Consumer Key):** `AqILOzu2sc0ACsA54IIzjesbGziGqURt`
- ✅ **Affiliate ID:** `6497023`

---

## 🔧 **Configuration:**

### **Step 1: Add to Local Environment**

**Edit your `.env` file** and add these lines:

```bash
# Ticketmaster API (for concert/sports events)
TICKETMASTER_API_KEY=AqILOzu2sc0ACsA54IIzjesbGziGqURt
TICKETMASTER_AFFILIATE_ID=6497023
```

### **Step 2: Add to Production (Railway)**

1. **Go to Railway dashboard**
2. **Click on "wonderful-vibrancy" (your API service)**
3. **Go to "Variables" tab**
4. **Add these variables:**
   - **Name:** `TICKETMASTER_API_KEY`  
     **Value:** `AqILOzu2sc0ACsA54IIzjesbGziGqURt`
   
   - **Name:** `TICKETMASTER_AFFILIATE_ID`  
     **Value:** `6497023`

5. **Railway will automatically redeploy with new variables**

---

## 🚀 **Testing Locally:**

### **Option 1: Test the Extractor Directly**

```powershell
cd worker
python extractors/ticketmaster.py
```

**Expected output:**
```
🎫 Fetching Ticketmaster events for Dallas, TX...
✅ Found 150+ events from Ticketmaster
✅ Successfully parsed 150+ Ticketmaster events

📊 Total events extracted: 150+
```

### **Option 2: Test via Dashboard**

1. **Make sure your services are running:**
   ```powershell
   docker-compose up -d
   ```

2. **Go to:** http://localhost:3001

3. **Login with:** `admin@firstindallas.com` / `admin123`

4. **Go to "Bulk Sync" page**

5. **Click "Sync Ticketmaster Events"** button

6. **Wait 30-60 seconds**

7. **Go to "Events" page** - you should see new Ticketmaster events!

---

## 💰 **Affiliate Tracking:**

### **How It Works:**

Every Ticketmaster event URL automatically includes your affiliate ID:

**Example event URL:**
```
https://www.ticketmaster.com/some-concert-tickets/event/123?CAMEFROM=CMPAFFILIATE_6497023
```

**When someone:**
1. Clicks "Buy Tickets" on your website
2. Gets redirected to Ticketmaster with your affiliate link
3. Purchases a ticket within the session
4. **You earn commission!** 💰

**Commission rates:**
- **iOS app purchases:** 0.5% - 5%
- **Android app purchases:** 0.5% - 5%
- **Resale tickets:** 5%

---

## 📊 **What Events You'll Get:**

### **Event Types:**
- 🎵 **Music:** Concerts, festivals, club shows
- 🏈 **Sports:** Cowboys, Mavericks, Rangers, FC Dallas
- 🎭 **Theater:** Broadway shows, comedy, plays
- 🎬 **Film:** Screenings, film festivals
- 🎪 **Other:** Family events, exhibitions

### **Coverage Area:**
- **Dallas**
- **Fort Worth**
- **Arlington**
- **Plano**
- **50-mile radius**

### **Expected Volume:**
- **~100-200 events** at any given time
- **Fresh events daily**
- **API rate limit:** 5,000 requests/day (more than enough!)

---

## 🎯 **API Endpoints:**

### **Sync Ticketmaster Events**
```
POST /api/sync/ticketmaster/dallas
Headers: Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "message": "Ticketmaster bulk sync started",
  "task_id": 123,
  "status": "queued",
  "locations": ["Dallas", "Fort Worth", "Arlington", "Plano"],
  "radius": "50 miles",
  "categories": ["Music", "Sports", "Arts & Theatre", "Film"],
  "note": "Events include affiliate tracking for commission earnings"
}
```

### **Check Sync Status**
```
GET /api/sync/status
Headers: Authorization: Bearer YOUR_TOKEN
```

**Response includes `ticketmaster` array with recent sync tasks**

---

## 🔍 **Event Fields:**

Each Ticketmaster event includes:

```json
{
  "title": "Concert Name",
  "description": "Event description",
  "start_at": "2025-11-15T19:00:00",
  "venue": "American Airlines Center",
  "address": "2500 Victory Avenue",
  "city": "Dallas",
  "price_tier": "paid",
  "price_amount": "49.50",
  "image_url": "https://...",
  "source_url": "https://www.ticketmaster.com/...?CAMEFROM=CMPAFFILIATE_6497023",
  "source_type": "ticketmaster",
  "category": "Music"
}
```

---

## 📈 **Tracking Your Earnings:**

1. **Go to:** https://impact.com (Ticketmaster's affiliate platform)
2. **Login with your affiliate account**
3. **View dashboard for:**
   - Clicks
   - Conversions
   - Earnings
   - Commission breakdown

---

## 🎨 **Display on WordPress:**

Events automatically show on your WordPress events directory with:
- ✅ Event details
- ✅ "Buy Tickets" button → Opens Ticketmaster with YOUR affiliate link
- ✅ Ticketmaster logo/badge
- ✅ Price information
- ✅ Venue details

---

## 🐛 **Troubleshooting:**

### **Issue: No events synced**

**Check:**
1. Environment variables are set correctly
2. API key is valid (test at: https://developer.ticketmaster.com/)
3. Worker is running: `docker-compose ps`
4. Check worker logs: `docker-compose logs worker`

### **Issue: API rate limit exceeded**

**Solution:**
- Free tier: 5,000 requests/day
- One sync uses ~5-10 requests
- You can sync 500-1000 times/day
- If you hit limits, wait 24 hours or upgrade plan

### **Issue: Affiliate links not working**

**Check:**
1. `TICKETMASTER_AFFILIATE_ID` is set in environment
2. Event `source_url` contains `?CAMEFROM=CMPAFFILIATE_6497023`
3. Test a link manually in browser
4. Check Impact.com dashboard for tracking

---

## 📚 **Additional Resources:**

- **Ticketmaster API Docs:** https://developer.ticketmaster.com/products-and-docs/apis/getting-started/
- **Affiliate Dashboard:** https://impact.com
- **Event Discovery API:** https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/

---

## 🎉 **You're All Set!**

Your Events CMS now includes:
- ✅ Facebook events (Apify)
- ✅ Eventbrite events (Official API)
- ✅ **Ticketmaster events (Official API + Affiliate) 💰**

**Next steps:**
1. Add environment variables
2. Sync Ticketmaster events
3. Display on your website
4. **Start earning commission!** 🚀

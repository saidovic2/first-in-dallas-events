# 🎫 Ticketmaster Integration Guide

## Overview
Your Events CMS has a complete Ticketmaster Discovery API integration with affiliate tracking! This allows you to:
- ✅ Import events automatically from Dallas-Fort Worth area
- ✅ Earn commissions through affiliate tracking
- ✅ Access 230K+ events (concerts, sports, theater, family events)
- ✅ 5000 API calls per day quota

---

## 🔑 Your Credentials

From your Ticketmaster Developer Portal (images provided):

- **Consumer Key (API Key)**: `Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK`
- **Affiliate ID**: `6497023` (via Impact - for earning commissions!)
- **Rate Limit**: 5000 requests/day, 5 requests/second
- **Status**: ✅ Approved (Public APIs enabled)

These are already configured in your `.env` file.

---

## 📂 Integration Architecture

### 1. **Worker/Extractor** (`worker/extractors/ticketmaster.py`)
- Fetches events from Ticketmaster Discovery API
- Parses event data (title, date, venue, price, images)
- Adds affiliate tracking to event URLs for commission
- Handles 200 events per request
- Maps Ticketmaster categories to your system

**Key Features:**
```python
- City/state search (Dallas, TX with 50-mile radius)
- Price tier detection (FREE/PAID/PREMIUM)
- Image extraction (highest quality)
- Venue & location data
- Category mapping (Music, Sports, Arts, Film)
- Affiliate URL tracking
```

### 2. **API Service** (`api/services/ticketmaster.py`)
- Provides reusable Ticketmaster API methods
- Event search with filters
- Event details lookup
- Transforms Ticketmaster data to your database format

### 3. **API Routes** (`api/routes/ticketmaster.py`)
**Endpoints:**
- `GET /api/ticketmaster/search` - Search Ticketmaster events
- `GET /api/ticketmaster/event/{id}` - Get event details
- `POST /api/ticketmaster/import/{id}` - Import single event
- `POST /api/ticketmaster/bulk-import` - Bulk import multiple events

### 4. **Sync Routes** (`api/routes/sync.py`)
**Bulk Sync Endpoint:**
- `POST /api/sync/ticketmaster/dallas` - Bulk sync Dallas events
- Creates background task in Redis queue
- Worker processes the task asynchronously
- Returns task_id for status tracking

### 5. **Frontend UI** (`web/app/(dashboard)/sync/page.tsx`)
- **Ticketmaster Sync Card** - Already added!
- Shows last sync status
- Loading states & progress tracking
- Success/error messaging

---

## 🚀 How to Use

### **Option 1: Via Dashboard (Easiest)**
1. Go to your CMS dashboard → **Sync** page
2. Find the **Ticketmaster Sync Card** (purple card with 🎫)
3. Click **"🎫 Sync Ticketmaster Events"**
4. Wait 1-2 minutes while events are imported
5. View imported events in the **Events** page

### **Option 2: Via API**
```bash
# Start bulk sync
curl -X POST "http://your-api-url/api/sync/ticketmaster/dallas" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "message": "Ticketmaster bulk sync started",
  "task_id": 123,
  "status": "queued"
}

# Check sync status
curl "http://your-api-url/api/sync/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Option 3: Direct API Search**
```bash
# Search for specific events
curl "http://your-api-url/api/ticketmaster/search?city=Dallas&state_code=TX&classification=music&size=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 What Events Are Imported

### Categories Covered:
1. **🎵 Music** - Concerts, festivals, live music
2. **⚽ Sports** - Cowboys, Mavericks, Stars, Rangers, FC Dallas
3. **🎭 Arts & Theatre** - Plays, musicals, ballet, opera
4. **🎬 Film** - Movie screenings, film festivals
5. **👨‍👩‍👧 Family** - Kids shows, family entertainment

### Search Area:
- **Primary**: Dallas, TX
- **Radius**: 50 miles (covers Fort Worth, Plano, Arlington, etc.)
- **Expected Results**: 100-300+ active events

### Event Data Extracted:
- ✅ Title & description
- ✅ Date & time
- ✅ Venue name & full address
- ✅ Price information (min/max)
- ✅ High-resolution images
- ✅ Event URL **with affiliate tracking** (earn commissions!)
- ✅ Category classification
- ✅ Geographic coordinates

---

## 💰 Affiliate Commission Tracking

### How It Works:
Your Ticketmaster Affiliate ID (`6497023`) is automatically added to all event URLs:

**Original URL:**
```
https://www.ticketmaster.com/event/ABC123
```

**With Your Affiliate Tracking:**
```
https://www.ticketmaster.com/event/ABC123?CAMEFROM=CMPAFFILIATE_6497023
```

### Commission Structure:
When users click through your site and buy tickets, you earn a commission! Check your Impact dashboard for earnings.

**Tracking code location:** `worker/extractors/ticketmaster.py` lines 163-166

---

## 🔍 Ticketmaster API Details

### Base URL:
```
https://app.ticketmaster.com/discovery/v2/
```

### Key Endpoints Used:
1. **Event Search**: `/events.json`
   - Filters: city, state, radius, classification, date range
   - Pagination: size (max 200), page (max 1000 items total)
   - Sorting: by date, name, relevance

2. **Event Details**: `/events/{id}.json`
   - Full event information
   - Venue details
   - Images & pricing
   - Attractions (artists/teams)

### Rate Limits:
- **Daily**: 5000 requests
- **Per Second**: 5 requests
- **Deep Paging**: Max 1000 items (size × page < 1000)

### Best Practices:
✅ Cache results to minimize API calls  
✅ Use bulk import (200 events per call) vs individual imports  
✅ Schedule syncs during off-peak hours  
✅ Monitor rate limits in API responses  

---

## 🛠️ Configuration

### Environment Variables (.env):
```bash
# Ticketmaster API (already configured!)
TICKETMASTER_API_KEY=Tx3dcKearAsHFOrhBsO6JVK2HbT0AEoK
TICKETMASTER_AFFILIATE_ID=6497023
```

### Model Configuration:
The `ticketmaster_bulk` source type is already added to your models:
- ✅ `api/models/event.py`
- ✅ `api/models/task.py`
- ✅ `worker/models/event.py`
- ✅ `worker/models/task.py`

---

## 🧪 Testing

### Test the Extractor:
```bash
cd worker
python extractors/ticketmaster.py
```

This will:
- Fetch 200 Dallas events
- Display sample event data
- Show parsing results

### Test the API Service:
```bash
cd api
python services/ticketmaster.py
```

### Test the Full Sync:
1. Start the API: `uvicorn main:app --reload`
2. Start the worker: `python worker/worker.py`
3. Trigger sync via dashboard or cURL
4. Watch logs for progress

---

## 📈 Monitoring & Troubleshooting

### Check Sync Status:
```bash
GET /api/sync/status
```

Returns:
```json
{
  "ticketmaster": [
    {
      "id": 123,
      "status": "completed",
      "created_at": "2025-11-07T17:00:00",
      "completed_at": "2025-11-07T17:02:00",
      "logs": "✅ Successfully parsed 187 Ticketmaster events"
    }
  ]
}
```

### Common Issues:

**❌ "Invalid API Key"**
- Check `.env` has correct `TICKETMASTER_API_KEY`
- Verify key is active in Ticketmaster Developer Portal

**❌ "Rate Limit Exceeded"**
- You've hit 5000 requests/day or 5 requests/second
- Wait until quota resets (midnight UTC)
- Reduce sync frequency

**❌ "No Events Found"**
- Check city/state spelling
- Verify events exist for that location
- Try wider radius (e.g., 75 miles)

**❌ "Affiliate ID Not Working"**
- Confirm affiliate ID `6497023` is active in Impact dashboard
- Check URL format includes `CAMEFROM=CMPAFFILIATE_{id}`
- Test URLs manually to verify tracking

---

## 🎯 Recommended Sync Strategy

### Daily Schedule:
```
Morning (8 AM): Sync Eventbrite (fast, ~30s)
Afternoon (2 PM): Sync Ticketmaster (slower, ~2min)
Evening (8 PM): Sync Instagram posts (manual)
```

### Event Volume Expectations:
- **Eventbrite**: 50-150 events (Dallas organizers)
- **Ticketmaster**: 150-300 events (all categories)
- **Total**: 200-450 unique events (after deduplication)

### Deduplication:
Events are automatically deduplicated by:
- External ID (Ticketmaster event ID)
- Title + date + venue combination
- Prevents duplicate imports

---

## 📚 Additional Resources

### Ticketmaster Documentation:
- **Discovery API**: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- **Developer Portal**: https://developer.ticketmaster.com/
- **Affiliate Program**: https://Impact.com (check earnings)

### Your Implementation:
- **Worker**: `worker/extractors/ticketmaster.py`
- **API Service**: `api/services/ticketmaster.py`
- **Routes**: `api/routes/ticketmaster.py`, `api/routes/sync.py`
- **Frontend**: `web/app/(dashboard)/sync/page.tsx`

---

## ✅ Ready to Use!

Your Ticketmaster integration is **fully configured and operational**. Just click the sync button in your dashboard!

### Quick Start:
1. ✅ API credentials configured
2. ✅ Worker extractor ready
3. ✅ API endpoints active
4. ✅ Frontend UI deployed
5. ✅ Affiliate tracking enabled

**Next Step:** Go to your dashboard and click "🎫 Sync Ticketmaster Events"!

---

## 💡 Pro Tips

1. **Maximize Commissions**: Ensure event URLs are shared directly (contain affiliate tracking)
2. **Optimize Images**: Ticketmaster provides high-res images - use them for better engagement
3. **Category Filtering**: Use classification filters to focus on specific event types
4. **Price Display**: Show Ticketmaster prices prominently - helps with conversions
5. **Update Frequency**: Sync daily to keep events current and catch new additions

---

**Need help?** All code is documented and ready to customize!

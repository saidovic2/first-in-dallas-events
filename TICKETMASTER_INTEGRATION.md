# 🎟️ Ticketmaster API Integration Guide

## ✅ What We Built

A complete integration that allows you to:
1. **Search** Ticketmaster events by city, date, keyword
2. **Preview** events before importing
3. **Import** single events into your database
4. **Bulk import** multiple events at once
5. **Auto-transform** Ticketmaster data to match your schema

---

## 🔑 Step 1: Get Your Ticketmaster API Key (FREE)

### Register for API Access:

1. Go to: **https://developer.ticketmaster.com/**
2. Click **"Sign Up"** or **"Get Your API Key"**
3. Fill out the registration form:
   - Name
   - Email
   - Company/Project name: "First in Dallas Events"
   - Website (optional)
4. Click **"Create Account"**
5. **Instant approval!** You'll get your API key immediately

### Your Free Tier Includes:
- ✅ **5,000 API calls per day**
- ✅ **5 requests per second**
- ✅ **Access to 230K+ events**
- ✅ **Global coverage**
- ✅ **No credit card required**

---

## 🔧 Step 2: Add API Key to Your Environment

### Local Development:

Create/edit `.env` file in the `api` folder:

```bash
# api/.env
TICKETMASTER_API_KEY=your_api_key_here
```

### Production (Railway):

1. Go to **Railway Dashboard**
2. Click your API project
3. Go to **Variables** tab
4. Click **"+ New Variable"**
5. Add:
   - **Key:** `TICKETMASTER_API_KEY`
   - **Value:** `your_api_key_here`
6. **Redeploy** (automatic)

---

## 🚀 Step 3: How to Use the Integration

### **API Endpoints Added:**

#### 1. Search Ticketmaster Events
```
GET /api/ticketmaster/search?city=Dallas&state_code=TX
```

**Parameters:**
- `city` - City name (default: "Dallas")
- `state_code` - State code (default: "TX")
- `keyword` - Search keyword (optional)
- `classification` - Event type: "music", "sports", "arts" (optional)
- `size` - Results per page (default: 20, max: 200)
- `page` - Page number (default: 0)

**Example Response:**
```json
{
  "events": [
    {
      "id": "Z7r9jZ1AeXYkK",
      "name": "Dallas Mavericks vs. Lakers",
      "url": "https://www.ticketmaster.com/...",
      "dates": {
        "start": {
          "dateTime": "2024-11-15T19:00:00Z"
        }
      },
      "priceRanges": [
        {"min": 45.00, "max": 250.00}
      ],
      "_embedded": {
        "venues": [{
          "name": "American Airlines Center",
          "city": {"name": "Dallas"},
          "address": {"line1": "2500 Victory Ave"}
        }]
      }
    }
  ],
  "total": 150,
  "page": 0,
  "total_pages": 8
}
```

---

#### 2. Get Event Details
```
GET /api/ticketmaster/event/{event_id}
```

Returns full details for a specific event.

---

#### 3. Import Single Event
```
POST /api/ticketmaster/import/{event_id}
```

**What it does:**
1. Fetches event from Ticketmaster
2. Transforms data to match your database schema
3. Creates new event in your database
4. Returns success message

**Example Response:**
```json
{
  "message": "Successfully imported: Dallas Mavericks vs. Lakers",
  "event_id": 123,
  "title": "Dallas Mavericks vs. Lakers"
}
```

**Error if already exists:**
```json
{
  "detail": "Event already imported: Dallas Mavericks vs. Lakers"
}
```

---

#### 4. Bulk Import Events
```
POST /api/ticketmaster/bulk-import?city=Dallas&max_events=50
```

**Parameters:**
- `city` - City to import from
- `state_code` - State code
- `classification` - Filter by category (optional)
- `max_events` - Maximum events to import (default: 50, max: 200)

**What it does:**
1. Searches Ticketmaster for events
2. Checks each event if it already exists
3. Imports new events only
4. Skips duplicates
5. Returns summary

**Example Response:**
```json
{
  "message": "Bulk import complete",
  "imported": 35,
  "skipped": 15,
  "total_found": 50,
  "errors": []
}
```

---

## 🎨 Step 4: Add UI to Your CMS

### Option 1: Add "Import from Ticketmaster" Page

Create a new page in your CMS:
- Search Ticketmaster events
- Preview events in a table
- Click "Import" button to add to your database
- Bulk import with filters

### Option 2: Auto-Sync with Cron Job

Set up automatic daily imports:

```python
# Run daily at 2 AM
# Import all Dallas events for next 30 days
POST /api/ticketmaster/bulk-import?city=Dallas&max_events=100
```

---

## 📋 Step 5: Data Transformation

### Ticketmaster → Your Database Mapping:

| Ticketmaster Field | Your Database Field |
|-------------------|-------------------|
| `name` | `title` |
| `info` or `pleaseNote` | `description` |
| `url` | `primary_url` |
| `venues[0].name` | `venue` |
| `venues[0].address.line1` | `address` |
| `venues[0].city.name` | `city` |
| `venues[0].state.stateCode` | `state` |
| `venues[0].postalCode` | `zip_code` |
| `dates.start.dateTime` | `start_at` |
| `images[0].url` | `image_url` |
| `priceRanges[0].min` | `price_amount` |
| Auto-calculated | `price_tier` (FREE/PAID/PREMIUM) |
| `id` | `external_id` |
| "TICKETMASTER" | `source_type` |

---

## 🎯 Use Cases

### **Use Case 1: Manual Curation**
1. Search for "music" events in Dallas
2. Preview list of events
3. Select best events to import
4. Click "Import" for each

### **Use Case 2: Automated Aggregation**
1. Set up cron job to run daily
2. Auto-import all upcoming Dallas events
3. Review in CMS
4. Publish or reject

### **Use Case 3: Category-Specific**
1. Import only "sports" events for sports section
2. Import only "music" events for music section
3. Keep your directory organized by category

---

## 🔧 Advanced Features

### Filter by Date Range:
```python
# Import only events in next 7 days
results = tm_service.search_events(
    city="Dallas",
    start_date="2024-11-01T00:00:00Z",
    end_date="2024-11-07T23:59:59Z"
)
```

### Filter by Price:
Events are automatically categorized:
- **FREE**: No price ranges
- **PAID**: Min price < $50
- **PREMIUM**: Min price >= $50

### Prevent Duplicates:
The system checks `external_id` before importing.
If event already exists, it skips it.

---

## 📊 Statistics

**Available Data:**
- 230,000+ events
- Global coverage (US, Canada, UK, Australia, etc.)
- All categories: Music, Sports, Arts, Theater, Family
- Live, up-to-date information
- High-quality images

**For Dallas Alone:**
- ~500-1000 active events at any time
- Major venues covered (AAC, AT&T Stadium, etc.)
- All major artists and sports teams

---

## 🚀 Testing the Integration

### Test Locally:

1. **Start your API:**
```bash
cd api
uvicorn main:app --reload
```

2. **Open API docs:**
http://localhost:8000/docs

3. **Try the endpoints:**
   - Click "Authorize" and login
   - Go to "Ticketmaster" section
   - Try `/api/ticketmaster/search`
   - Import an event with `/api/ticketmaster/import/{id}`

---

## 📝 Implementation Checklist:

- [ ] Get Ticketmaster API key
- [ ] Add `TICKETMASTER_API_KEY` to Railway
- [ ] Deploy updated API
- [ ] Test search endpoint
- [ ] Test import endpoint
- [ ] Build CMS UI (optional)
- [ ] Set up auto-sync (optional)

---

## 💡 Pro Tips:

1. **Start with small batches** - Test with 5-10 events first
2. **Check for duplicates** - The system does it automatically
3. **Review before publishing** - Import as DRAFT first
4. **Use classification filters** - Keep your directory focused
5. **Set up monitoring** - Track how many events you import daily

---

## 🎉 Benefits:

✅ **Save hours of manual data entry**
✅ **Always up-to-date event information**
✅ **Professional-quality data**
✅ **High-resolution images included**
✅ **Accurate venue and pricing information**
✅ **SEO-friendly event URLs**
✅ **100% FREE (within quota)**

---

## 🔗 Useful Links:

- Ticketmaster API Docs: https://developer.ticketmaster.com/
- Discovery API Reference: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- API Explorer (Test Live): https://developer.ticketmaster.com/api-explorer/

---

**Ready to import thousands of events automatically?** 🚀

Just add your API key and you're good to go!

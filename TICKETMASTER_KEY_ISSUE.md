# 🔑 Ticketmaster API Key Issue - Troubleshooting

## Current Status
- ✅ App Created: "First in Dallas Events v2"
- ✅ Public APIs: Approved
- ✅ OAuth Product: Approved
- ❌ Key still returns 401 Unauthorized

## Your New Key
```
Consumer Key: 5J6gVlhTbffU8kyFbTL5jeIqpkorcmQO
Created: Fri, 11/07/2025 - 17:35
Expires: Never
```

---

## 🚨 Problem: Key Shows Approved but Still Unauthorized

### Possible Causes:

1. **Discovery API Product Not Added**
   - Your app is approved, but Discovery API might not be enabled
   - Solution: Add Discovery API product to your app

2. **Propagation Delay**
   - New keys can take 5-10 minutes to activate
   - Solution: Wait and try again

3. **Wrong API Product**
   - You might have approved "Public APIs" but need "Discovery API" specifically
   - Solution: Check which products are enabled

---

## ✅ Solutions to Try:

### Solution 1: Check API Products
1. In Ticketmaster Developer Portal
2. Click on your app: "First in Dallas Events v2"
3. Go to **"Details"** tab
4. Look for **"API Products"** or **"Products"** section
5. Check if **"Discovery API"** is listed
6. If not listed, click **"Add Product"** → Select **"Discovery API"**

### Solution 2: Create App from Discovery API Page
1. Go directly to: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
2. Click **"Get Your API Key"** button (should be prominent on page)
3. This creates an app with Discovery API pre-enabled
4. Fill out form:
   - App Name: `First in Dallas Events - Discovery`
   - Description: `Event aggregator using Discovery API`
   - Website: `https://firstindallas.com`
5. Get Consumer Key from new app

### Solution 3: Wait and Retry
Sometimes keys need time to propagate:
```powershell
# Wait 5 minutes, then test:
python test-ticketmaster-key.py
```

### Solution 4: Contact Support
If nothing works:
1. Go to: https://developer.ticketmaster.com/support/
2. Submit ticket: "API Key approved but returns 401"
3. Include your Consumer Key and app name

---

## 🧪 Testing Your Key

Run this anytime to test:
```powershell
python test-ticketmaster-key.py
```

Should show:
```
✅ SUCCESS! API key is valid!
✅ Found 5 events!
```

---

## 🎯 Once Working: Update Railway

When the key works:

1. **Go to Railway**: https://railway.app
2. **Click your API service** → **Variables**
3. **Update** `TICKETMASTER_API_KEY` to: `5J6gVlhTbffU8kyFbTL5jeIqpkorcmQO`
4. **Update worker service** (if separate) with same key
5. **Wait for redeploy** (2-3 minutes)
6. **Test sync** from your admin CMS

---

## 📊 Expected API Response When Working

```json
{
  "_embedded": {
    "events": [
      {
        "name": "Dallas Mavericks vs Phoenix Suns",
        "dates": {...},
        "venue": {...}
      }
    ]
  },
  "page": {
    "size": 5,
    "totalElements": 287,
    "totalPages": 58
  }
}
```

---

## 🔗 Useful Links

- **Discovery API Docs**: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
- **My Apps**: https://developer.ticketmaster.com/products-and-docs/apis/getting-started/
- **Support**: https://developer.ticketmaster.com/support/

---

## 💡 Quick Decision Tree

```
Is your key less than 10 minutes old?
├─ YES → Wait 10 minutes, then test again
└─ NO → Check if Discovery API product is enabled
    ├─ Can't find product settings → Create new app from Discovery API page
    └─ Discovery API enabled but still 401 → Contact Ticketmaster support
```

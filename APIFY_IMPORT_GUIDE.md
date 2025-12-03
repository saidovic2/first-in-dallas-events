# 🎫 Apify Ticketmaster Import Guide

## Quick Steps to Import New Apify Data

### 1️⃣ Run Your Apify Actor

1. Go to: https://console.apify.com/
2. Run your Ticketmaster scraper actor
3. Wait for it to complete
4. Copy the **Dataset ID** (not the Run ID!)

**Where to find Dataset ID:**
- Click on the completed run
- Look for **"Dataset"** section
- Copy the ID (looks like: `MFCwnLRBHTdcsJKpS`)

---

### 2️⃣ Update the Import Script

Open `import_ticketmaster_simple.py` and update line 18:

```python
# Change this line:
DATASET_ID = "MFCwnLRBHTdcsJKpS"  # OLD dataset

# To your new dataset ID:
DATASET_ID = "YOUR_NEW_DATASET_ID_HERE"
```

---

### 3️⃣ Run the Import

```powershell
python import_ticketmaster_simple.py
```

Or use auto-run (no prompt):
```powershell
python run_import.py
```

---

### 4️⃣ What Happens

The script will:
- ✅ **Import NEW events** that don't exist yet
- ✅ **Skip DUPLICATES** automatically (checks by URL + title + date)
- ✅ **Skip parking/valet** passes
- ✅ **Add affiliate tracking** to all URLs
- ✅ **Save as DRAFT** status

**Example Output:**
```
[1/250] Processing: ELENA ROSE - Alma US Tour 2025...
   [OK] Imported (ID: 1234)

[2/250] Processing: Dallas Mavericks vs Brooklyn Nets...
   >> Skipped (duplicate - already exists as ID 950)

[3/250] Processing: Valet Parking - Concert...
   >> Skipped (parking/valet/misc)

...

IMPORT SUMMARY
================================================================================
[OK] Imported: 150 events
[>>] Skipped (parking/valet): 25 events
[>>] Skipped (duplicates): 75 events
[ERROR] Errors: 0 events
```

---

## 🔍 How Duplicate Detection Works

### Unique Hash Generated:
```python
fid_hash = sha256(url + title + start_date)
```

**Same Event = Same Hash:**
- Same title
- Same URL
- Same date
→ **Detected as duplicate, skipped!**

**Different Event:**
- Different title OR
- Different URL OR  
- Different date
→ **Imported as new!**

---

## 📊 Multiple Imports (Safe!)

You can run the import script **as many times as you want**:

**1st Run:**
```
Imported: 180 events
Duplicates: 0 events
```

**2nd Run (same dataset):**
```
Imported: 0 events
Duplicates: 180 events  ← All skipped!
```

**2nd Run (new dataset):**
```
Imported: 95 events     ← Only new ones!
Duplicates: 85 events   ← Ones we had before
```

---

## 🎯 Best Practices

### Weekly Refresh
1. Run Apify actor weekly
2. Import new dataset
3. New events auto-imported
4. Duplicates auto-skipped

### After Big Updates
If Apify scrapes more venues:
1. Run actor with updated settings
2. Import the larger dataset
3. Only NEW events will be added

### Testing
Want to test without duplicates?
1. Delete some test events from CMS
2. Re-import dataset
3. Those events will be re-added

---

## 🔧 Advanced: Custom Filtering

### Import Only Specific Cities

Edit `transform_apify_event()` in `import_ticketmaster_simple.py`:

```python
# Skip events not in desired cities
city = apify_event.get('addressLocality', 'Dallas')
if city not in ['Dallas', 'Irving', 'Plano']:
    return None  # Skip this event
```

### Import Only Specific Categories

```python
# Skip events not in desired categories
segment = apify_event.get('segmentName', '')
if segment not in ['Music', 'Sports']:
    return None  # Skip this event
```

### Import Only Premium Events

```python
# Skip free/cheap events
price = apify_event.get('offer.price')
if price and float(price) < 50:
    return None  # Skip cheap events
```

---

## 🚨 Troubleshooting

### "Database connection refused"
**Fix:** Make sure DATABASE_URL is correct in the script

### "Invalid dataset ID"
**Fix:** 
1. Double-check the Dataset ID (not Run ID!)
2. Make sure Apify run completed successfully
3. Verify API token is correct

### "All events skipped as duplicates"
**Expected!** This means:
- All events already exist in database
- No new events to import
- Everything working correctly! ✅

### "ImportError: No module named..."
**Fix:** Install dependencies:
```powershell
pip install sqlalchemy psycopg2-binary python-dateutil requests
```

---

## 📝 Quick Reference

### Get Dataset from Apify API
```bash
curl "https://api.apify.com/v2/datasets/YOUR_DATASET_ID/items?token=YOUR_TOKEN"
```

### Check Database for Ticketmaster Events
```powershell
python check_ticketmaster_events.py
```

### View Import History
Check Railway logs or local console output for:
- How many imported
- How many duplicates
- Any errors

---

## 🎉 You're All Set!

**Process Summary:**
1. Run Apify → Get Dataset ID
2. Update script → New Dataset ID
3. Run import → New events added, duplicates skipped
4. Check CMS → See new DRAFT events
5. Publish or let auto-publish handle it!

**Need help?** Check the console output for detailed info on what happened.

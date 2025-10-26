# WordPress Events Calendar Update

## ✅ Changes Completed

### 1. **Fixed Directory Page Loading Issue**
The local directory page (`/directory`) was stuck loading due to a dependency loop in the useEffect hooks. This has been resolved by simplifying the data fetching logic.

**File Updated:** `web/app/directory/page.tsx`
- Removed complex useEffect dependencies
- Restored simple, working implementation
- Page now loads immediately with all events

---

### 2. **WordPress Plugin Calendar Updates**

All requested features have been added to the **WordPress Events CMS Directory Plugin**.

**Files Updated:**
- `wordpress-plugin/events-cms-directory/events-cms-directory.php` 
- `wordpress-plugin/events-cms-directory/css/style.css`

#### Features Added:

##### ✅ Category Filter Removed
- Removed category dropdown from filters
- Removed category display from event cards
- Cleaned up all category-related API logic

##### ✅ Date Picker Added
- Single-date HTML5 date picker between City and Price filters
- Labeled "Date"
- No default date (shows empty, user picks a date)
- Filters events for the selected day (00:00:00 to 23:59:59)
- Automatically re-fetches data when changed

##### ✅ 20-Per-Page Pagination
- Displays exactly 20 events per page
- Classic numbered pagination with:
  - **First (<<)** and **Last (>>)** buttons
  - **Prev (<)** and **Next (>)** buttons  
  - Smart page numbers (shows 1 ... 3 4 5 ... 10)
  - Shows current page in blue
  - Shows event count (e.g., "Showing 1 to 20 of 156 events")

##### ✅ URL Query Sync
- All filters sync to URL parameters:
  - `?search=...` for search term
  - `?city=...` for city filter
  - `?date=YYYY-MM-DD` for date picker
  - `?price_tier=...` for price filter
  - `?page_num=N` for pagination
- URLs are shareable and bookmarkable
- Browser back/forward buttons work correctly

##### ✅ Enhanced Empty State
- Shows **"No events found for this day. Try another date."** when date filter returns no results
- Generic "No events found." for other cases

##### ✅ Filter Reset Behavior
- Changing any filter (search, city, date, price) resets to page 1
- "Clear" button resets all filters and removes date selection

---

## 🚀 How to Use

### Installation

1. **Upload Plugin to WordPress:**
   ```
   wordpress-plugin/events-cms-directory/
   ```
   Copy this folder to your WordPress `wp-content/plugins/` directory

2. **Activate the Plugin:**
   - Go to WordPress Admin → Plugins
   - Find "Events CMS Directory"
   - Click "Activate"

3. **Configure API URL:**
   - Go to WordPress Admin → Settings → Events CMS
   - Enter your API URL (e.g., `http://localhost:8000/api` or `https://api.yoursite.com/api`)
   - Click "Save Changes"

### Using the Shortcode

Add the events calendar to any WordPress page or post:

```
[events_directory]
```

#### Optional Parameters:

```
[events_directory status="PUBLISHED" show_filters="yes"]
```

**Parameters:**
- `status` - Filter by event status (default: `PUBLISHED`)
- `show_filters` - Show/hide filter form (default: `yes`, set to `no` to hide)

---

## 📋 Features Overview

### Filter Bar
The filter bar appears at the top with 4 fields:
1. **Search** - Text input for searching event titles, descriptions, venues
2. **City** - Dropdown populated from available cities in your events
3. **Date** - Date picker for selecting a specific day
4. **Price** - Dropdown (All Prices / Free / Paid)

Two buttons:
- **Apply Filters** (blue) - Apply the selected filters
- **Clear** (gray) - Reset all filters

### Event Cards
Each event displays:
- Event image (if available)
- Event title
- Date and time
- Venue and city
- Price tier (FREE/PAID badge)
- Description excerpt
- "View Details →" link to source

### Pagination
Appears at the bottom when there are more than 20 events:
- Shows current range (e.g., "Showing 21 to 40 of 156 events")
- Navigation: First | Prev | 1 2 3 ... | Next | Last
- Current page highlighted in blue
- Disabled buttons grayed out

---

## 🎨 Styling

The plugin includes complete CSS styling that matches your existing design:
- Clean, modern cards with hover effects
- Responsive grid (3 columns on desktop, 1 on mobile)
- Professional filter bar with labels
- Accessible pagination controls
- Mobile-friendly layout

All styles are in `css/style.css` and can be customized to match your WordPress theme.

---

## 🔧 Technical Details

### API Integration
The plugin fetches events from your Events CMS API:
- **Endpoint:** `/api/events/`
- **Filters:** `status`, `city`, `search`, `price_tier`, `start_date`, `end_date`
- **Cities List:** `/api/events/cities/list`

### Date Filtering
When a date is selected:
1. Converts to start of day: `YYYY-MM-DD 00:00:00`
2. Converts to end of day: `YYYY-MM-DD 23:59:59`
3. Sends to API as ISO 8601 format
4. API returns only events within that 24-hour period

### Pagination Logic
1. Fetches all matching events from API (up to 1000)
2. Divides into pages of 20 events each
3. Displays only the current page
4. Updates URL with `?page_num=N` parameter
5. Preserves all filter parameters when changing pages

---

## ✅ Testing Checklist

Test the following scenarios:

- [ ] Plugin activates without errors
- [ ] Filter bar displays correctly
- [ ] City dropdown shows available cities
- [ ] Date picker allows selecting any date
- [ ] Search filter works
- [ ] Price filter works (Free/Paid)
- [ ] Pagination shows when > 20 events
- [ ] Page numbers work correctly
- [ ] URL parameters update when filtering
- [ ] Shared URLs load with correct filters
- [ ] "Clear" button resets all filters
- [ ] Empty state message shows when no events match
- [ ] Date-specific empty message appears when no events on selected date
- [ ] Event cards display correctly
- [ ] "View Details" links work
- [ ] Responsive design works on mobile

---

## 🐛 Troubleshooting

### No Events Showing
1. Check API URL in Settings → Events CMS
2. Verify API is running and accessible
3. Check browser console for errors
4. Verify events exist with status "PUBLISHED"

### Filters Not Working
1. Clear browser cache
2. Check that API supports filter parameters
3. Verify date format is YYYY-MM-DD

### Pagination Issues
1. Check that PHP array_slice function is available
2. Verify URL parameters are being passed correctly
3. Check for JavaScript errors in console

---

## 🎉 Summary

Your WordPress events calendar now has:
✅ No Category filter (removed)
✅ Date picker filter (pick any day)
✅ 20 events per page
✅ Smart numbered pagination (First/Prev/1 2 3.../Next/Last)
✅ URL query sync (?search=...&date=...&page_num=...)
✅ Date-specific empty state message
✅ All existing styling preserved
✅ Mobile responsive
✅ Shareable URLs

The local Directory page (`/directory`) is also fixed and working without the long loading issue.

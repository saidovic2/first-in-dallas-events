# Events Sidebar Widget Setup

## Overview

A new **Upcoming Events** sidebar widget has been added to the Events CMS Directory WordPress plugin. This widget displays upcoming events in a clean, sidebar-friendly format with thumbnail images and dates.

## Features

- 📌 Displays 5 upcoming events by default (configurable)
- 🖼️ Shows event thumbnail images (80x80px)
- 📅 Displays event titles and dates
- 🔗 Links to event source URLs
- ⚡ Automatically filters for upcoming published events
- 📱 Responsive and mobile-friendly design

## Installation & Setup

### 1. Update the Plugin

Run the update script to copy the latest plugin files to WordPress:

```powershell
.\update-wordpress-plugin.ps1
```

### 2. Add Widget to Sidebar

1. Log into your WordPress admin panel
2. Navigate to **Appearance → Widgets**
3. Find the **"Upcoming Events"** widget in the available widgets list
4. Drag it to your desired widget area (e.g., Primary Sidebar, Footer, etc.)

### 3. Configure Widget

In the widget settings, you can configure:

- **Title**: The heading for the widget (default: "Events")
- **Number of events**: How many upcoming events to display (1-10, default: 5)

## Widget Display

The widget shows events in a vertical list format, similar to a blog post sidebar:

```
┌─────────────────────────────┐
│         Events              │
├─────────────────────────────┤
│ [IMG]  Event Title          │
│        January 27, 2025     │
├─────────────────────────────┤
│ [IMG]  Another Event        │
│        January 28, 2025     │
├─────────────────────────────┤
│ [IMG]  Third Event          │
│        January 29, 2025     │
└─────────────────────────────┘
```

## Technical Details

### Widget Class
- **Class Name**: `EventsCMS_Upcoming_Events_Widget`
- **Widget ID**: `eventscms_upcoming_events`
- **Widget Name**: "Upcoming Events"

### Data Fetching
- Fetches events from the configured Events CMS API
- Filters for `PUBLISHED` status only
- Filters events where `start_at >= current date/time`
- Sorts by date (earliest first)
- Limits to the specified number of events

### Styling
The widget includes custom CSS classes:

- `.eventscms-widget-events` - Container for all events
- `.eventscms-widget-event` - Individual event item
- `.eventscms-widget-event-image` - Event thumbnail (80x80px)
- `.eventscms-widget-event-content` - Event text content
- `.eventscms-widget-event-title` - Event title/link
- `.eventscms-widget-event-date` - Event date

## Customization

### Changing Number of Events

You can modify the default number of events in the widget settings, or programmatically via filters (if needed in the future).

### Styling

To customize the widget appearance, you can:

1. Edit `wordpress-plugin/events-cms-directory/css/style.css`
2. Or add custom CSS in your theme's stylesheet
3. Use WordPress Customizer's Additional CSS

Example custom styling:

```css
/* Change widget background color */
.widget_eventscms_upcoming_events {
    background: #f8f9fa;
}

/* Change image size */
.eventscms-widget-event-image {
    width: 100px;
    height: 100px;
}

/* Change title color on hover */
.eventscms-widget-event-title a:hover {
    color: #ff6b6b;
}
```

## API Requirements

The widget uses the same API configuration as the main plugin:

- **API URL**: Set in WordPress Settings → Events CMS
- **Endpoint**: `GET /api/events`
- **Parameters**: `?status=PUBLISHED&limit={number}`

Ensure your Events CMS API is running and accessible.

## Troubleshooting

### Widget doesn't appear
- Ensure your theme has widget areas/sidebars
- Check that the plugin is activated
- Verify the widget is added to a widget area

### No events displayed
- Check that you have upcoming published events in your CMS
- Verify the API URL in Settings → Events CMS
- Check that events have `start_at` dates in the future
- Ensure events have images (optional, but recommended)

### Images not loading
- Verify event `image_url` fields are valid
- Check that images are accessible from your WordPress site
- Check browser console for CORS or loading errors

## Files Modified

The following files were modified/created for this feature:

```
wordpress-plugin/events-cms-directory/
├── events-cms-directory.php    (Added widget class and registration)
├── css/style.css                (Added widget styles)
└── README.txt                   (Updated documentation)
```

## Next Steps

1. ✅ Run the update script: `.\update-wordpress-plugin.ps1`
2. ✅ Add the widget to your sidebar via WordPress admin
3. ✅ Configure the widget title and number of events
4. ✅ View your site to see the upcoming events widget in action!

---

**Created**: 2025-01-30  
**Version**: 1.0.0  
**Plugin**: Events CMS Directory

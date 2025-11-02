# Events CMS Directory - WordPress Plugin

A WordPress plugin that displays events from your Events CMS API on WordPress pages using shortcodes and widgets.

## Features

- 📅 Display events from your Events CMS API
- 🎨 Beautiful, responsive grid layout
- 🔍 Filter events by city, date, and price
- ⚡ Fast API integration
- 📱 Mobile-friendly design
- 🎯 Simple shortcode implementation
- 📌 Sidebar widget for upcoming events

## Installation

### From GitHub

1. Download the latest release ZIP from [Releases](https://github.com/saidovic2/events-cms-directory/releases)
2. In WordPress admin, go to Plugins → Add New → Upload Plugin
3. Choose the downloaded ZIP file
4. Click Install Now
5. Activate the plugin

### Manual Installation

1. Clone this repository or download as ZIP
2. Upload the `events-cms-directory` folder to `/wp-content/plugins/`
3. Activate the plugin through the 'Plugins' menu in WordPress
4. Configure API URL in Settings → Events CMS

## Configuration

### API Setup

1. Go to Settings → Events CMS in WordPress admin
2. Enter your Events CMS API URL (e.g., `https://api.firstindallas.com/api`)
3. Save settings

### Using the Shortcode

Display events on any page or post:

```
[events_directory]
```

The shortcode includes built-in filters for:
- Search
- City selection
- Date picker
- Price tier (Free/Paid)

### Using the Widget

1. Go to Appearance → Widgets
2. Find "Upcoming Events" widget
3. Drag to your desired widget area (sidebar, footer, etc.)
4. Configure:
   - **Title**: Widget heading (e.g., "Upcoming Events")
   - **Number of events**: 1-10 events (default: 5)
   - **Calendar Page URL**: Link for "See events Calendar" button
   - **Submit Event Page URL**: Link for "Submit Your event" button
5. Save

The widget displays:
- Event thumbnail images
- Event titles (clickable)
- Event dates
- Two action buttons at the bottom

## Requirements

- WordPress 5.0 or higher
- PHP 7.4 or higher
- Active Events CMS API

## Auto-Updates via GitHub

This plugin supports automatic updates from GitHub releases. To enable:

1. Install [GitHub Updater](https://github.com/afragen/github-updater) plugin
2. The plugin will automatically check for updates
3. Update notifications will appear in WordPress admin

## Changelog

### Version 1.1.0 (2025-11-02)
- ✅ Fixed constructor method from `__init()` to `__construct()`
- ✅ Added Upcoming Events sidebar widget
- ✅ Added two action buttons to widget (Calendar & Submit Event)
- ✅ Improved GitHub integration for auto-updates

### Version 1.0.0 (2025-10-30)
- Initial release
- Event directory shortcode
- Grid layout with responsive design
- City, date, and price filtering
- Settings page for API configuration

## Support

For issues or feature requests, please [open an issue](https://github.com/saidovic2/events-cms-directory/issues) on GitHub.

## License

This plugin is licensed under GPL2.

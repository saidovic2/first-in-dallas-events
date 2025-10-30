=== Events CMS Directory ===
Contributors: yourname
Tags: events, directory, calendar, cms, api
Requires at least: 5.0
Tested up to: 6.4
Stable tag: 1.0.0
Requires PHP: 7.4
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Display events from your Events CMS on WordPress pages using shortcodes.

== Description ==

Events CMS Directory is a WordPress plugin that seamlessly integrates with your Events CMS application to display beautiful event listings on your WordPress website.

**Features:**

* 📅 Display events from your Events CMS API
* 🎨 Beautiful, responsive grid layout
* 🔍 Filter events by city, category, and status
* ⚡ Fast API integration
* 📱 Mobile-friendly design
* 🎯 Simple shortcode implementation
* 📌 Sidebar widget for upcoming events

**How to Use:**

Add the events directory to any page using:
`[events_directory]`

**Shortcode Parameters:**

* `limit` - Number of events to display (default: 20)
* `city` - Filter by city name
* `category` - Filter by category
* `status` - Filter by event status (PUBLISHED or DRAFT)
* `source_type` - Filter by event source

**Examples:**

Show all events:
`[events_directory]`

Show 10 events from Dallas:
`[events_directory city="Dallas" limit="10"]`

Show only music events:
`[events_directory category="Music"]`

Show Facebook events only:
`[events_directory source_type="facebook" limit="15"]`

**Sidebar Widget:**

Add the "Upcoming Events" widget to any widget area:
1. Go to Appearance → Widgets
2. Find "Upcoming Events" widget
3. Drag it to your desired widget area (sidebar, footer, etc.)
4. Configure the title and number of events to display (default: 5)

The widget will automatically display the next upcoming published events with their images and dates.

== Installation ==

1. Upload the `events-cms-directory` folder to `/wp-content/plugins/`
2. Activate the plugin through the 'Plugins' menu in WordPress
3. Go to Settings → Events CMS to configure your API URL
4. Add `[events_directory]` shortcode to any page

== Frequently Asked Questions ==

= What is Events CMS? =

Events CMS is a centralized event management system that aggregates events from multiple sources like Facebook, Eventbrite, and more.

= Do I need an Events CMS installation? =

Yes, this plugin requires a running Events CMS API to fetch event data.

= How do I set up the API connection? =

Go to Settings → Events CMS in WordPress admin and enter your Events CMS API URL (e.g., http://localhost:8001/api or https://api.yoursite.com/api)

= Can I customize the event display? =

Yes! You can modify the CSS file in the plugin folder or use WordPress customizer to override styles.

= What if events don't appear? =

1. Check that your Events CMS API is running
2. Verify the API URL in plugin settings
3. Ensure events are set to PUBLISHED status
4. Check browser console for errors

== Screenshots ==

1. Events grid display
2. Plugin settings page
3. Event card detail
4. Mobile responsive view

== Changelog ==

= 1.0.0 =
* Initial release
* Event directory shortcode
* Grid layout with responsive design
* City, category, and status filtering
* Settings page for API configuration
* Upcoming Events sidebar widget

== Upgrade Notice ==

= 1.0.0 =
Initial release of Events CMS Directory plugin.

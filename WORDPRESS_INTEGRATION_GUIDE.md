# 🎯 WordPress Integration Guide

Complete step-by-step guide to integrate your Events CMS with WordPress.

---

## 📋 **Table of Contents**

1. [Prerequisites](#prerequisites)
2. [Method 1: Display Events Directory (Recommended)](#method-1-display-events-directory)
3. [Method 2: Publish Individual Events](#method-2-publish-individual-events)
4. [Troubleshooting](#troubleshooting)

---

## ✅ **Prerequisites**

Before starting, ensure you have:

- [x] WordPress installed locally (using Local by Flywheel, XAMPP, or WAMP)
- [x] Events CMS running (API at http://localhost:8001)
- [x] WordPress admin access
- [x] Basic knowledge of WordPress plugins

---

## 🎨 **Method 1: Display Events Directory** (Recommended)

This method creates a beautiful events directory page on your WordPress site using a shortcode.

### **Step 1: Install WordPress Locally**

If you don't have WordPress installed yet:

#### Option A: Using Local by Flywheel (Easiest)
1. Download **Local** from https://localwp.com/
2. Install and open Local
3. Click **+ Create a new site**
4. Name it: `my-events-site`
5. Choose **Preferred** environment
6. Set admin username/password
7. Click **Add Site**

#### Option B: Using XAMPP
1. Download XAMPP from https://www.apachefriends.org/
2. Install XAMPP
3. Start Apache and MySQL
4. Download WordPress from https://wordpress.org/
5. Extract to `C:\xampp\htdocs\wordpress`
6. Visit http://localhost/wordpress and follow installation

### **Step 2: Install the Events CMS Plugin**

1. **Copy the plugin folder:**
   ```powershell
   # From PowerShell
   cp -r "c:\Users\HP\Desktop\FiD- Events CMS\wordpress-plugin\events-cms-directory" "C:\path\to\wordpress\wp-content\plugins\"
   ```

   Replace `C:\path\to\wordpress\` with your WordPress installation path:
   - **Local by Flywheel**: `C:\Users\HP\Local Sites\my-events-site\app\public\wp-content\plugins\`
   - **XAMPP**: `C:\xampp\htdocs\wordpress\wp-content\plugins\`

2. **Login to WordPress Admin:**
   - Visit: http://your-wordpress-site/wp-admin
   - Login with your admin credentials

3. **Activate the Plugin:**
   - Go to **Plugins** → **Installed Plugins**
   - Find "Events CMS Directory"
   - Click **Activate**

### **Step 3: Configure the Plugin**

1. **Go to Settings:**
   - Click **Settings** → **Events CMS** in WordPress admin

2. **Set API URL:**
   ```
   http://localhost:8001/api
   ```
   
   **Important:** If WordPress and Events CMS are on the same machine, use:
   - `http://localhost:8001/api` ✅
   - `http://127.0.0.1:8001/api` ✅
   - NOT `http://192.168.x.x:8001/api` (may cause CORS issues)

3. **Save Changes**

### **Step 4: Create Events Page**

1. **Create a new page:**
   - Go to **Pages** → **Add New**
   - Title: `Events`

2. **Add the shortcode:**
   ```
   [events_directory]
   ```

3. **Optional - Add filters:**
   ```
   [events_directory city="Dallas" limit="20"]
   ```
   
   or
   
   ```
   [events_directory category="Music" status="PUBLISHED"]
   ```

4. **Publish the page**

5. **View your events:**
   - Visit: http://your-wordpress-site/events

### **Step 5: Customize (Optional)**

#### Available Shortcode Parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `limit` | Number of events to show | `limit="20"` |
| `city` | Filter by city | `city="Dallas"` |
| `category` | Filter by category | `category="Music"` |
| `status` | Filter by status | `status="PUBLISHED"` |
| `source_type` | Filter by source | `source_type="facebook"` |

#### Example Shortcodes:

**Show all events:**
```
[events_directory]
```

**Show 10 Dallas events:**
```
[events_directory city="Dallas" limit="10"]
```

**Show only music events:**
```
[events_directory category="Music"]
```

**Show Facebook events only:**
```
[events_directory source_type="facebook" limit="15"]
```

---

## 📤 **Method 2: Publish Individual Events to WordPress**

This method publishes selected events as WordPress posts.

### **Step 1: Enable WordPress REST API**

1. **Login to WordPress Admin**

2. **Create Application Password:**
   - Go to **Users** → **Profile**
   - Scroll to **Application Passwords**
   - Name: `Events CMS`
   - Click **Add New Application Password**
   - **Copy the generated password** (you'll only see it once!)

### **Step 2: Configure Events CMS**

1. **Open your .env file:**
   ```powershell
   notepad "c:\Users\HP\Desktop\FiD- Events CMS\.env"
   ```

2. **Add WordPress credentials:**
   ```env
   # WordPress Integration
   WP_BASE_URL=http://your-wordpress-site.com
   WP_USER=admin
   WP_APP_PASSWORD=your-app-password-here
   ```

   Replace:
   - `http://your-wordpress-site.com` with your WordPress URL
   - `admin` with your WordPress username
   - `your-app-password-here` with the application password

3. **Save and close**

4. **Restart API:**
   ```powershell
   docker-compose restart api
   ```

### **Step 3: Publish Events from Dashboard**

1. **Go to Events CMS Dashboard:**
   - Visit: http://localhost:3001/events

2. **Find an event you want to publish**

3. **Click "Publish to WordPress"** button

4. **Check WordPress:**
   - Go to your WordPress **Posts**
   - The event should appear as a new post!

---

## 🔧 **Troubleshooting**

### **Issue: "Unable to load events" message**

**Solution:**
1. Check if Events CMS API is running:
   ```powershell
   docker-compose ps
   ```
   
2. Verify API is accessible:
   - Visit: http://localhost:8001/api/events
   - Should show JSON data

3. Check CORS settings in `api/main.py`:
   ```python
   allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost"]
   ```

### **Issue: No events showing**

**Solution:**
1. Ensure events are PUBLISHED (not DRAFT):
   ```powershell
   docker-compose exec -T db psql -U postgres -d events_cms -c "UPDATE events SET status = 'PUBLISHED' WHERE status = 'DRAFT';"
   ```

2. Check API response:
   - Visit: http://localhost:8001/api/events?status=PUBLISHED

### **Issue: Plugin not appearing in WordPress**

**Solution:**
1. Verify plugin folder structure:
   ```
   wp-content/
   └── plugins/
       └── events-cms-directory/
           ├── events-cms-directory.php
           └── css/
               └── style.css
   ```

2. Check file permissions

3. Deactivate and reactivate the plugin

### **Issue: WordPress REST API authentication fails**

**Solution:**
1. Regenerate Application Password
2. Ensure no spaces in password when copying
3. Check username is correct
4. Test REST API:
   ```powershell
   curl -u "admin:your-app-password" http://localhost/wp-json/wp/v2/posts
   ```

### **Issue: Events not styled correctly**

**Solution:**
1. Ensure CSS file exists at:
   `wp-content/plugins/events-cms-directory/css/style.css`

2. Clear WordPress cache
3. Hard refresh browser (Ctrl + Shift + R)

---

## 🎨 **Customization**

### **Change Event Card Design**

Edit: `wordpress-plugin/events-cms-directory/css/style.css`

### **Modify Event Display**

Edit: `wordpress-plugin/events-cms-directory/events-cms-directory.php`

Look for the `generate_events_html()` function

### **Add Custom Fields**

Modify the API call in `fetch_events()` to include additional parameters

---

## 📚 **Next Steps**

1. ✅ Set up WordPress locally
2. ✅ Install and configure the plugin
3. ✅ Create an Events page
4. ✅ Add the shortcode
5. ✅ Customize as needed
6. 🚀 Deploy to production when ready!

---

## 💡 **Tips**

- Use **status="PUBLISHED"** in shortcode to show only published events
- Combine multiple filters for targeted event lists
- Create multiple event pages for different categories
- Use WordPress page builders (Elementor, etc.) for more design control

---

## 🆘 **Need Help?**

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Verify all prerequisites are met
3. Ensure Events CMS is running
4. Check WordPress error logs

---

**Happy Event Publishing! 🎉**

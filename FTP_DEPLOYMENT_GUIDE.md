# FTP Deployment Guide for WordPress Plugin

This guide explains how to deploy your WordPress plugin updates via FTP, alongside your API (Railway) and CMS (Vercel) deployments.

## 🎯 Overview

Your new deployment workflow:

1. **API (Railway)** - Push to Railway via Git or Railway CLI
2. **CMS (Vercel)** - Deploy via Vercel CLI or auto-deploy from GitHub
3. **WordPress Plugin (FTP)** - Deploy directly to WordPress server via FTP

This replaces the previous GitHub-based WordPress plugin update system that wasn't working properly.

---

## 📋 Prerequisites

### Required
- PowerShell (included with Windows)
- FTP credentials for your WordPress hosting server

### Optional (for better reliability)
- **WinSCP** - For more reliable FTP transfers
  - Download: https://winscp.net/eng/download.php
  - The script will auto-detect and use WinSCP if installed

### For Full Workflow
- **Railway CLI** (optional) - For API deployments
  ```bash
  npm install -g @railway/cli
  railway login
  railway link
  ```

- **Vercel CLI** (optional) - For CMS deployments
  ```bash
  npm install -g vercel
  vercel login
  cd hub && vercel link
  ```

---

## ⚙️ Setup

### 1. Configure FTP Credentials

1. Copy `.env.example` to `.env` if you haven't already:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Open `.env` and add your FTP credentials:
   ```env
   FTP_HOST=your-wordpress-server.com
   FTP_PORT=21
   FTP_USER=your-ftp-username
   FTP_PASSWORD=your-ftp-password
   FTP_REMOTE_PATH=/wp-content/plugins/events-cms-directory
   ```

### 2. Get Your FTP Credentials

Most hosting providers (cPanel, Plesk, etc.) provide FTP access:

**For cPanel:**
1. Log into cPanel
2. Go to "FTP Accounts"
3. Create a new FTP account or use your main account
4. Note the FTP server address, username, and password

**For other hosting:**
- Check your hosting provider's documentation for FTP access
- Look for "FTP", "File Manager", or "SFTP" settings

### 3. Verify FTP Path

The default path is `/wp-content/plugins/events-cms-directory`. Verify this is correct for your WordPress installation:
- Some hosts use `/public_html/wp-content/plugins/`
- Others might use `/httpdocs/wp-content/plugins/`

---

## 🚀 Deployment Options

### Option 1: Deploy Everything at Once (Recommended)

Deploy API, CMS, and WordPress Plugin together:

```powershell
# Deploy everything with plugin version update
.\deploy-all.ps1 -PluginVersion "1.2.0" -CommitMessage "Update all components"

# Deploy everything without changing plugin version
.\deploy-all.ps1 -CommitMessage "Update all components"
```

### Option 2: Deploy Plugin Only

Deploy just the WordPress plugin via FTP:

```powershell
# With version update
.\deploy-plugin-ftp.ps1 -Version "1.2.0"

# Without version update
.\deploy-plugin-ftp.ps1 -SkipVersionUpdate
```

### Option 3: Deploy Specific Component

```powershell
# Deploy only API to Railway
.\deploy-all.ps1 -Target api

# Deploy only CMS to Vercel
.\deploy-all.ps1 -Target cms

# Deploy only Plugin via FTP
.\deploy-all.ps1 -Target plugin -PluginVersion "1.2.0"
```

---

## 📝 Typical Workflow

### Making Plugin Updates

1. **Edit your plugin files** in `wordpress-plugin/events-cms-directory/`

2. **Test locally** (if you have a local WordPress setup)

3. **Deploy via FTP:**
   ```powershell
   # Quick deploy without version change
   .\deploy-plugin-ftp.ps1 -SkipVersionUpdate
   
   # Or with version update
   .\deploy-plugin-ftp.ps1 -Version "1.2.3"
   ```

4. **Activate changes in WordPress:**
   - Log into your WordPress admin panel
   - Go to Plugins page
   - Deactivate and reactivate "Events CMS Directory"
   - Or use WP-CLI: `wp plugin deactivate events-cms-directory && wp plugin activate events-cms-directory`

### Making API Updates

1. **Edit your API files** in `api/`

2. **Deploy to Railway:**
   ```powershell
   .\deploy-all.ps1 -Target api -CommitMessage "Update API endpoints"
   ```

3. **Monitor deployment** at Railway dashboard

### Making CMS Updates

1. **Edit your CMS files** in `hub/`

2. **Deploy to Vercel:**
   ```powershell
   .\deploy-all.ps1 -Target cms -CommitMessage "Update CMS UI"
   ```

3. **Verify deployment** at Vercel dashboard

### Full Stack Updates

When you've made changes across multiple components:

```powershell
.\deploy-all.ps1 -PluginVersion "1.3.0" -CommitMessage "Feature: Add new event filters"
```

---

## 🔍 Troubleshooting

### FTP Connection Issues

**Problem:** "ERROR: FTP credentials not configured!"
- **Solution:** Make sure your `.env` file exists and has FTP credentials filled in

**Problem:** "Cannot connect to FTP server"
- **Solution:** 
  - Verify your FTP_HOST is correct
  - Check if FTP_PORT is correct (usually 21 for FTP, 22 for SFTP)
  - Confirm your username and password are correct
  - Check if your hosting provider blocks FTP (some use SFTP only)

**Problem:** "Permission denied when uploading files"
- **Solution:** 
  - Verify your FTP user has write permissions
  - Check that FTP_REMOTE_PATH is correct and writable

### Plugin Not Updating

**Problem:** Changes deployed but not showing in WordPress
- **Solution:** 
  1. Clear WordPress cache (if using caching plugin)
  2. Deactivate and reactivate the plugin
  3. Hard refresh your browser (Ctrl+F5)
  4. Check if files actually uploaded by browsing via FTP client

### WinSCP Issues

**Problem:** Want to use WinSCP but script doesn't detect it
- **Solution:** Install WinSCP to default location: `C:\Program Files (x86)\WinSCP\`
- Alternative: The script falls back to PowerShell FTP (works but slower)

### Version Number Not Updating

**Problem:** Version number in WordPress doesn't change
- **Solution:** 
  - Make sure you're using `-Version` parameter, not `-SkipVersionUpdate`
  - Check that the version was updated in the PHP file
  - Deactivate and reactivate the plugin in WordPress

---

## 🎓 Best Practices

### 1. Version Management
- Use semantic versioning: `MAJOR.MINOR.PATCH`
  - `MAJOR`: Breaking changes
  - `MINOR`: New features, backwards compatible
  - `PATCH`: Bug fixes

### 2. Commit Messages
- Use descriptive commit messages
- Examples:
  - `"Fix: Calendar widget date display"`
  - `"Feature: Add event search functionality"`
  - `"Update: Improve API error handling"`

### 3. Testing
- Always test plugin changes locally first if possible
- Keep a staging WordPress site for testing
- Have backups before deploying major changes

### 4. Deployment Frequency
- Deploy plugin updates as needed (FTP is instant)
- Group related changes together
- Deploy API/CMS updates during low-traffic periods if making breaking changes

### 5. Security
- **Never commit your `.env` file to Git**
- Keep FTP credentials secure
- Use strong passwords for FTP access
- Consider using SFTP (port 22) instead of FTP if your host supports it

---

## 📊 Deployment Comparison

| Method | Old (Git Updater) | New (FTP) |
|--------|-------------------|-----------|
| **Speed** | Slow (via GitHub release) | Instant |
| **Reliability** | Issues with WordPress not detecting | Direct file upload |
| **Process** | 4+ steps, manual release | 1 command |
| **Testing** | Must release to test | Can deploy to test |
| **Rollback** | Create new release | Re-upload previous version |

---

## 🔗 Quick Reference

### Essential Commands

```powershell
# Deploy everything
.\deploy-all.ps1 -PluginVersion "1.2.0"

# Plugin only (quick update)
.\deploy-plugin-ftp.ps1 -SkipVersionUpdate

# API only
.\deploy-all.ps1 -Target api

# CMS only
.\deploy-all.ps1 -Target cms

# Plugin only (with version)
.\deploy-all.ps1 -Target plugin -PluginVersion "1.2.0"
```

### FTP Connection String Format
```
ftp://username:password@hostname:port/path
```

### WordPress Plugin Path (typical)
```
/wp-content/plugins/events-cms-directory/
```

---

## 📞 Getting Help

If you encounter issues:

1. Check the error message in the PowerShell output
2. Verify your FTP credentials are correct
3. Test FTP connection with FileZilla or another FTP client
4. Check your hosting provider's documentation for FTP access
5. Ensure the remote path exists and is writable

---

## 🎉 Success!

You now have a streamlined deployment workflow that:
- ✅ Deploys plugin updates instantly via FTP
- ✅ Bypasses GitHub release complications
- ✅ Supports API and CMS deployments in one command
- ✅ Provides clear feedback and error messages
- ✅ Works reliably every time

Happy deploying! 🚀

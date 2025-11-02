# GitHub Plugin Setup Guide

Complete guide to push your WordPress plugin to GitHub and enable auto-updates.

## 📋 Prerequisites

- GitHub account
- Git installed on your computer
- Plugin files ready in: `wordpress-plugin\events-cms-directory\`

---

## 🚀 Step 1: Create GitHub Repository

### On GitHub.com:

1. **Go to** https://github.com/new

2. **Repository settings:**
   - **Repository name**: `events-cms-directory`
   - **Description**: "WordPress plugin for displaying Events CMS events"
   - **Visibility**: Choose **Private** or **Public**
   - ✅ Do NOT initialize with README (we already have one)
   - ✅ Do NOT add .gitignore (we already have one)

3. **Click** "Create repository"

4. **Copy the repository URL** - you'll need this:
   ```
   https://github.com/saidovic2/events-cms-directory.git
   ```

---

## 💻 Step 2: Initialize Git & Push to GitHub

### Open PowerShell in the plugin directory:

```powershell
cd "C:\Users\HP\Desktop\FiD- Events CMS\wordpress-plugin\events-cms-directory"
```

### Initialize Git repository:

```powershell
git init
```

### Add your GitHub username and email:

```powershell
git config user.name "saidovic2"
git config user.email "your-email@example.com"
```

### Add all files:

```powershell
git add .
```

### Create first commit:

```powershell
git commit -m "Initial commit - Events CMS Directory Plugin v1.1.0"
```

### Add GitHub remote:

```powershell
git remote add origin https://github.com/saidovic2/events-cms-directory.git
```

### Push to GitHub:

```powershell
git branch -M main
git push -u origin main
```

**Note**: You may be prompted to log in to GitHub. Use your GitHub credentials.

---

## 🏷️ Step 3: Create a Release (For Auto-Updates)

### On GitHub.com:

1. **Go to your repository**: https://github.com/saidovic2/events-cms-directory

2. **Click** "Releases" (right sidebar)

3. **Click** "Create a new release"

4. **Tag settings:**
   - **Choose a tag**: Type `v1.1.0` and click "Create new tag: v1.1.0 on publish"
   - **Release title**: `Version 1.1.0 - Widget Support`
   - **Description**:
     ```
     ## What's New
     - Fixed critical constructor bug
     - Added Upcoming Events sidebar widget
     - Added action buttons to widget
     - GitHub auto-update support
     
     ## Installation
     Download the ZIP file below and upload via WordPress admin.
     ```

5. **Click** "Publish release"

6. **Download the auto-generated ZIP** (e.g., `events-cms-directory-1.1.0.zip`)

---

## 🔄 Step 4: Enable Auto-Updates in WordPress

You have **two options** for auto-updates:

### **Option A: Using GitHub Updater Plugin (Recommended)**

1. **Install GitHub Updater:**
   - Download from: https://github.com/afragen/github-updater/releases
   - Upload to WordPress: Plugins → Add New → Upload Plugin
   - Activate

2. **Your plugin will automatically be detected** because it has the `GitHub Plugin URI` header

3. **WordPress will now show update notifications** when you create new releases on GitHub

### **Option B: Manual Update Each Time**

1. Create a new release on GitHub (with version bump)
2. Download the release ZIP
3. Upload via WordPress: Plugins → Add New → Upload Plugin → Replace

---

## 📝 Step 5: Making Updates (Workflow)

### When you make changes to the plugin:

#### 1. Update Version Number

Edit `events-cms-directory.php` header:
```php
* Version: 1.2.0
```

#### 2. Commit Changes

```powershell
cd "C:\Users\HP\Desktop\FiD- Events CMS\wordpress-plugin\events-cms-directory"
git add .
git commit -m "Update: Description of changes"
git push origin main
```

#### 3. Create New Release on GitHub

1. Go to Releases → Create a new release
2. Tag: `v1.2.0`
3. Title: `Version 1.2.0 - Feature Name`
4. Description: List changes
5. Publish release

#### 4. WordPress Will Auto-Detect Update

If using GitHub Updater, WordPress will show "Update Available" in:
- Dashboard → Updates
- Plugins page

---

## 🎯 Quick Commands Reference

### First Time Setup:
```powershell
cd "C:\Users\HP\Desktop\FiD- Events CMS\wordpress-plugin\events-cms-directory"
git init
git config user.name "saidovic2"
git config user.email "your-email@example.com"
git add .
git commit -m "Initial commit - Events CMS Directory Plugin v1.1.0"
git remote add origin https://github.com/saidovic2/events-cms-directory.git
git branch -M main
git push -u origin main
```

### For Future Updates:
```powershell
cd "C:\Users\HP\Desktop\FiD- Events CMS\wordpress-plugin\events-cms-directory"
git add .
git commit -m "Description of changes"
git push origin main
```

Then create a new release on GitHub with bumped version number.

---

## ✅ Checklist

- [ ] GitHub repository created
- [ ] Git initialized and pushed
- [ ] First release (v1.1.0) created on GitHub
- [ ] Plugin uploaded to live WordPress site
- [ ] GitHub Updater plugin installed (optional but recommended)
- [ ] Test update detection in WordPress

---

## 🔧 Troubleshooting

### Git asks for authentication:
- Use GitHub Personal Access Token instead of password
- Generate at: https://github.com/settings/tokens
- Use token as password when prompted

### Updates not showing in WordPress:
- Make sure GitHub Updater plugin is installed and activated
- Check plugin headers have `GitHub Plugin URI` field
- Verify release tag matches version number format (`v1.1.0`)

### Permission denied when pushing:
- Check you're logged in to correct GitHub account
- Verify repository exists and you have write access

---

## 📚 Resources

- **GitHub Updater Plugin**: https://github.com/afragen/github-updater
- **Git Documentation**: https://git-scm.com/doc
- **WordPress Plugin Handbook**: https://developer.wordpress.org/plugins/

---

**Created**: 2025-11-02  
**Plugin Version**: 1.1.0  
**Repository**: https://github.com/saidovic2/events-cms-directory

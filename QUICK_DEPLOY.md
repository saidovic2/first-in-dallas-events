# Quick Deploy Reference

## 🚀 Setup (One Time Only)

1. **Copy environment file:**
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Add FTP credentials to `.env`:**
   ```env
   FTP_HOST=your-server.com
   FTP_USER=your-username
   FTP_PASSWORD=your-password
   FTP_REMOTE_PATH=/wp-content/plugins/events-cms-directory
   ```

3. **Done!** You're ready to deploy.

---

## 📦 Common Deployments

### Deploy Everything
```powershell
.\deploy-all.ps1 -PluginVersion "1.2.0" -CommitMessage "Your update description"
```

### Plugin Only (Quick Update)
```powershell
.\deploy-plugin-ftp.ps1 -SkipVersionUpdate
```

### Plugin with Version Update
```powershell
.\deploy-plugin-ftp.ps1 -Version "1.2.0"
```

### API Only
```powershell
.\deploy-all.ps1 -Target api -CommitMessage "API update"
```

### CMS Only
```powershell
.\deploy-all.ps1 -Target cms -CommitMessage "CMS update"
```

---

## ✅ After Plugin Deploy

1. Go to WordPress admin panel
2. Navigate to Plugins
3. Deactivate "Events CMS Directory"
4. Activate "Events CMS Directory"
5. Done!

---

## 🔧 Troubleshooting

**FTP not connecting?**
- Check credentials in `.env`
- Verify FTP_HOST and FTP_REMOTE_PATH are correct
- Try connecting with FileZilla to test

**Plugin not updating?**
- Deactivate and reactivate in WordPress
- Clear WordPress cache
- Hard refresh browser (Ctrl+F5)

---

## 📖 Full Documentation

For detailed information, see: `FTP_DEPLOYMENT_GUIDE.md`

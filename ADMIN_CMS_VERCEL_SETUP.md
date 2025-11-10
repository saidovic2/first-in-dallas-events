# 🎛️ Admin CMS - Vercel Deployment Setup

## ✅ Deployment Status

Your Admin CMS (with Ticketmaster sync) has been deployed to Vercel!

**Production URL**: https://first-in-dallas-cms.vercel.app (or your assigned URL)

---

## ⚙️ Required: Set Environment Variables

The CMS won't work without these environment variables. Add them in Vercel:

### **Step 1: Go to Environment Variables**
https://vercel.com/saids-projects-cee94186/first-in-dallas-cms/settings/environment-variables

### **Step 2: Add These Variables**

Click "Add New" for each:

#### **1. NEXT_PUBLIC_API_URL**
```
https://wonderful-vibrancy-production.up.railway.app
```
- Environment: Production, Preview, Development (all)

#### **2. NEXT_PUBLIC_SUPABASE_URL**
```
https://jwlvikkbcjrnzsvhyfgy.supabase.co
```
- Environment: Production, Preview, Development (all)

#### **3. NEXT_PUBLIC_SUPABASE_ANON_KEY**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp3bHZpa2tiY2pybnpzdmh5Zmd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0NjM3NzIsImV4cCI6MjA3NzAzOTc3Mn0.mRluKwZ2B0qg0Z8YGYCx4QRFMP5WwxiTef_olGDEJS4
```
- Environment: Production, Preview, Development (all)

### **Step 3: Redeploy**
After adding variables:
1. Go to: **Deployments** tab
2. Click **"..."** (three dots) on the latest deployment
3. Click **"Redeploy"**
4. Wait 1-2 minutes

---

## 🎯 Access Your Admin CMS

Once environment variables are set and redeployed:

### **Login URL:**
```
https://your-admin-cms-url.vercel.app/login
```

### **Default Admin Credentials:**
- Email: admin@firstindallas.com
- Password: [your admin password]

### **Navigate to Sync:**
1. Login to admin CMS
2. Go to: **Dashboard** → **Sync**
3. You'll see:
   - 🟢 **Eventbrite Sync**
   - 🎫 **Ticketmaster Sync** ✅

---

## 📊 Your Complete Deployment

```
🌐 Hub (Organizer Portal)
├─ URL: https://first-in-dallas-hub.vercel.app
└─ Purpose: Public event submissions

🎛️ Admin CMS (with Ticketmaster Sync)
├─ URL: https://first-in-dallas-cms.vercel.app ✅ NEW!
└─ Purpose: Event management, Ticketmaster sync

☁️ API (Backend)
├─ URL: https://wonderful-vibrancy-production.up.railway.app
└─ Purpose: Database, processing, workers
```

---

## 🔒 Security Note

Your admin CMS is now publicly accessible. Make sure to:
- ✅ Use strong admin passwords
- ✅ Only share admin credentials with trusted team members
- ✅ Monitor login activity
- 💡 Consider adding IP restrictions in Vercel if needed

---

## 🎫 Using Ticketmaster Sync

Once deployed and configured:

1. **Login** to your admin CMS
2. **Navigate** to Sync page
3. **Click** "🎫 Sync Ticketmaster Events"
4. **Wait** 1-2 minutes
5. **View** 100-300+ imported events!

All events will include your affiliate tracking ID (`6497023`) for commission earnings!

---

## 🚨 Troubleshooting

### **Error: "API connection failed"**
- Check that `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Verify Railway API is running: https://wonderful-vibrancy-production.up.railway.app/docs

### **Error: "Authentication failed"**
- Check Supabase environment variables are correct
- Verify Supabase project is active

### **Ticketmaster sync not working**
- Check Railway API has Ticketmaster credentials in its .env
- Verify worker is running on Railway
- Check Redis is configured

---

## ✅ Next Steps

1. **Set environment variables** (see Step 2 above)
2. **Redeploy** the admin CMS
3. **Login** and test Ticketmaster sync
4. **Share** the admin URL with your team

---

**Your admin CMS with Ticketmaster sync is now hosted and accessible from anywhere!** 🎉

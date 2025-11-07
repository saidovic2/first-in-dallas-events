# 🎛️ Start Admin CMS (with Ticketmaster Sync)

## Quick Start

The **Admin CMS** with Ticketmaster sync is in the `web/` directory and runs locally.

### Option 1: Using Docker (Recommended)
```powershell
# Start everything (API + Worker + Admin CMS)
docker-compose up -d

# Access the admin CMS at:
# http://localhost:3001
```

### Option 2: Manual Start
```powershell
# 1. Start API (in one terminal)
cd api
uvicorn main:app --reload --port 8001

# 2. Start Worker (in another terminal)  
cd worker
python worker.py

# 3. Start Admin CMS (in another terminal)
cd web
npm install
npm run dev

# Access at: http://localhost:3000
```

---

## 🔑 Admin Login

Default admin credentials (create if doesn't exist):
```
Email: admin@firstindallas.com
Password: [your password]
```

Or create admin via script:
```powershell
.\create-admin.ps1
```

---

## 📍 Where to Find Sync

Once logged in to the Admin CMS:
1. Navigate to: **Dashboard** → **Sync**
2. You'll see cards for:
   - 🟢 Eventbrite Sync
   - 🎫 Ticketmaster Sync (with your affiliate tracking!)
3. Click **"Sync Ticketmaster Events"**
4. Wait 1-2 minutes for ~200 events to import

---

## 🌐 Your Deployed Apps

**Organizer Portal (hub/)**: https://first-in-dallas-hub.vercel.app
- For public event submissions

**Admin CMS (web/)**: http://localhost:3000
- For managing events, running syncs
- Not deployed publicly (runs locally)

---

## 🚀 Alternative: Deploy Admin CMS

If you want the admin CMS hosted online:

### Deploy to Vercel (separate project):
```powershell
cd web
vercel --prod
```

This creates a second Vercel deployment just for admin.

**Important**: Set these environment variables in Vercel:
- `NEXT_PUBLIC_API_URL` = Your Railway API URL
- `NEXT_PUBLIC_SUPABASE_URL` = Your Supabase URL  
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` = Your Supabase anon key

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────┐
│  HUB (Vercel - Public)              │
│  hub.firstindallas.com              │
│  ➜ Organizer submissions            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  WEB (Local - Admin Only)           │
│  http://localhost:3000              │
│  ➜ Ticketmaster sync                │
│  ➜ Event management                 │
│  ➜ Admin controls                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  API (Railway - Backend)            │
│  wonderful-vibrancy.railway.app     │
│  ➜ Both apps connect here           │
└─────────────────────────────────────┘
```

---

## ✅ Next Steps

1. **Start the admin CMS**: `docker-compose up` or manual start
2. **Go to**: http://localhost:3000
3. **Login** with admin credentials
4. **Navigate to Sync** page
5. **Click Ticketmaster sync button**!

The Ticketmaster integration is fully ready - you just need to access the admin CMS!

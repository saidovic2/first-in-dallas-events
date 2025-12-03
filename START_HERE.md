# 🚀 START HERE - Local Event CMS

## Welcome! Your event management platform is ready.

### 📋 Prerequisites Check

Before starting, ensure you have:
- ✅ **Docker Desktop** installed and running
- ✅ **PowerShell** (comes with Windows)

### 🎯 Three Simple Steps

#### Step 1: Open PowerShell
Right-click in this folder and select "Open in Terminal" or "Open PowerShell window here"

#### START HERE - Railway Services Not Working (5 Minutes to Fix)
```powershell
.\setup.ps1
```
This will take 2-3 minutes to:
- Build Docker containers
- Start all services
- Initialize database with sample data

#### Step 3: Open Browser
Go to: **http://localhost:3000**

Login with:
- **Email**: `admin@example.com`
- **Password**: `admin123`

---

## 🎨 What You'll See

### 1️⃣ Dashboard (http://localhost:3000/dashboard)
Your command center showing:
- 📊 Events this week
- 📈 Extraction statistics
- 🌍 Top cities
- ⚠️ Recent errors

### 2️⃣ Add Events (http://localhost:3000/add)
Paste URLs to extract events:
```
Example URLs to try:
- Any webpage with event schema
- .ics calendar file
- RSS feed with events
```

### 3️⃣ Manage Events (http://localhost:3000/events)
Review and edit extracted events:
- ✏️ Edit details
- ✅ Publish/unpublish
- 🗑️ Delete
- 🔍 Search and filter

### 4️⃣ Public Directory (http://localhost:3000/directory)
Beautiful public-facing event listing:
- 🎯 Filter by city, category, price
- 🔍 Search events
- 📱 Grid or list view
- 🖼️ Event cards with images

---

## 🎮 Try These Actions

### Action 1: View Sample Events
1. Login at http://localhost:3000
2. Go to **Dashboard** - see 6 sample events
3. Go to **Manage Events** - view event details
4. Go to **Public Directory** - see how events appear to users

### Action 2: Extract an Event
1. Go to **Add Events**
2. Paste a URL (any webpage with event data)
3. Click **Extract Events**
4. Watch the task process
5. Go to **Manage Events** to see the result

### Action 3: Publish an Event
1. Go to **Manage Events**
2. Find a draft event
3. Click **Publish**
4. Go to **Public Directory** to see it live

---

## 📊 Sample Data Included

Your system comes with 6 events:

1. **Summer Music Festival 2024** 🎵
   - New York | Paid | Music

2. **Tech Startup Networking Mixer** 💼
   - San Francisco | Free | Business

3. **Community Yoga in the Park** 🧘
   - Portland | Free | Health & Wellness

4. **Local Art Gallery Opening** 🎨
   - Chicago | Free | Arts & Culture

5. **Food Truck Festival** 🍔
   - Seattle | Free | Food & Drink

6. **Charity Run for Education** 🏃
   - Boston | Paid | Sports

---

## 🔧 Quick Commands

### Start Application
```powershell
.\start.ps1
```

### Stop Application
```powershell
.\stop.ps1
```

### View Logs
```powershell
docker-compose logs -f
```

### Check Status
```powershell
docker-compose ps
```

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main web interface |
| **API** | http://localhost:8000 | Backend API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Dashboard** | http://localhost:3000/dashboard | Admin dashboard |
| **Public Directory** | http://localhost:3000/directory | Public event listing |

---

## 🆘 Troubleshooting

### "Port already in use"
Another service is using ports 3000, 8000, 5432, or 6379.
```powershell
# Stop other services or change ports in docker-compose.yml
```

### "Docker not found"
Install Docker Desktop from: https://www.docker.com/products/docker-desktop

### "Cannot connect to API"
```powershell
# Check if API is running
docker-compose ps api

# Restart API
docker-compose restart api
```

### "No events showing"
```powershell
# Reinitialize database
docker-compose exec api python init_db.py
```

---

## 📚 Documentation

- **QUICKSTART.md** - Quick reference guide
- **GETTING_STARTED.md** - Detailed setup and features
- **PROJECT_SUMMARY.md** - Complete project overview
- **README.md** - Technical documentation

---

## 🎯 Next Steps

1. ✅ **Run the setup** - `.\setup.ps1`
2. ✅ **Login** - http://localhost:3000
3. ✅ **Explore the dashboard** - See sample data
4. ✅ **Try adding an event** - Paste a URL
5. ✅ **Customize** - Edit styles, add features
6. ✅ **Deploy** - When ready for production

---

## 💡 Tips

- **Sample Data**: 6 events are pre-loaded for testing
- **API Docs**: Visit /docs for interactive API testing
- **Logs**: Use `docker-compose logs -f` to debug
- **WordPress**: Optional - configure in .env file
- **Customization**: Edit TailwindCSS config for styling

---

## 🎉 You're All Set!

Your Local Event CMS is ready to use. Start by running:

```powershell
.\setup.ps1
```

Then open http://localhost:3000 and login with:
- Email: `admin@example.com`
- Password: `admin123`

**Enjoy building your event platform!** 🚀

---

## 📞 Need Help?

1. Check the logs: `docker-compose logs -f`
2. Review API docs: http://localhost:8000/docs
3. Read GETTING_STARTED.md for detailed guides
4. Check PROJECT_SUMMARY.md for technical details

---

**Made with ❤️ for local event management**

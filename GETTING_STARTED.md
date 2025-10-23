# Getting Started with Local Event CMS

## 🚀 Quick Start (Recommended)

The fastest way to get started is using Docker:

```powershell
# Run setup (first time only)
.\setup.ps1

# Start the application
.\start.ps1
```

Then open http://localhost:3000 and login with:
- Email: `admin@example.com`
- Password: `admin123`

## 📋 What You'll See

### 1. Login Page
Clean authentication interface with default credentials displayed.

### 2. Dashboard
- **Events This Week**: Count of recently added events
- **Total Extractions**: Number of URL extraction tasks
- **Active Sources**: Monitored event sources
- **Failed Tasks**: Tasks requiring attention
- **Charts**: Events by status, top cities, top sources
- **Recent Errors**: Latest extraction failures

### 3. Add Events Page
- Paste one or multiple URLs
- Auto-detects source type (Facebook, Instagram, ICS, RSS, webpage)
- Queues background extraction tasks
- Shows extraction status in real-time

### 4. Manage Events Page
- Table view of all events
- Filter by status (draft/published)
- Search functionality
- Edit event details inline
- Publish/unpublish events
- Push to WordPress
- Delete events

### 5. Public Directory Page
- Public-facing event listing
- Filter by city, category, price tier
- Search events
- Grid and list view modes
- Beautiful event cards with images

## 🎯 Try These Actions

### Extract an Event from a URL

1. Go to **Add Events**
2. Paste a URL with event data (try these examples):
   - Any webpage with JSON-LD Event schema
   - An .ics calendar file URL
   - An RSS feed with event posts
3. Click **Extract Events**
4. Watch the task status update

### Manage Your Events

1. Go to **Manage Events**
2. Review the sample events
3. Click **Publish** to make an event public
4. Click **Push to WordPress** (requires WP setup)
5. Edit event details by clicking the edit icon

### View Public Directory

1. Go to **Public Directory** (or open http://localhost:3000/directory in a new tab)
2. This is what your users will see
3. Try filtering by city or category
4. Switch between grid and list views

## 🔧 Configuration

### Environment Variables

Edit `.env` file to customize:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/events_cms

# JWT Secret (change in production!)
JWT_SECRET=your-secret-key-change-in-production

# WordPress Integration (optional)
WP_BASE_URL=https://your-site.com
WP_USER=admin
WP_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### WordPress Setup

To enable WordPress publishing:

1. Install WordPress REST API (included in WP 4.7+)
2. Create an Application Password:
   - Go to Users → Profile
   - Scroll to "Application Passwords"
   - Create new password
3. Add credentials to `.env`
4. Restart API: `docker-compose restart api`

## 📊 Sample Data

The system includes 6 pre-populated events:

1. **Summer Music Festival 2024** - New York (Paid, Music)
2. **Tech Startup Networking Mixer** - San Francisco (Free, Business)
3. **Community Yoga in the Park** - Portland (Free, Health & Wellness)
4. **Local Art Gallery Opening** - Chicago (Free, Arts & Culture)
5. **Food Truck Festival** - Seattle (Free, Food & Drink)
6. **Charity Run for Education** - Boston (Paid, Sports)

## 🛠️ Architecture

```
┌─────────────┐
│   Next.js   │  Frontend (React, TypeScript, TailwindCSS)
│   Web App   │  Routes: /dashboard, /add, /events, /directory
└──────┬──────┘
       │ HTTP
       ↓
┌─────────────┐
│   FastAPI   │  Backend API (Python)
│   Server    │  Endpoints: /auth, /events, /tasks, /stats
└──────┬──────┘
       │
       ├──→ PostgreSQL (Events, Tasks, Users)
       ├──→ Redis (Task Queue)
       │
       ↓
┌─────────────┐
│   Worker    │  Background Processor (Python)
│   Process   │  Extractors: JSON-LD, ICS, RSS, HTML
└─────────────┘
```

## 🔍 Supported Event Sources

### 1. JSON-LD Structured Data
Websites with `<script type="application/ld+json">` containing Event schema.

**Example**:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Concert in the Park",
  "startDate": "2024-06-15T19:00",
  "location": {
    "@type": "Place",
    "name": "Central Park",
    "address": "New York, NY"
  }
}
</script>
```

### 2. ICS/iCal Files
Calendar files (.ics) with event data.

### 3. RSS/Atom Feeds
News feeds or event feeds in RSS/Atom format.

### 4. Facebook Events
Facebook event pages (requires public events).

### 5. Instagram Posts
Instagram posts with event information.

### 6. Generic Webpages
Fallback extraction using Open Graph tags and meta data.

## 🐛 Troubleshooting

### "Cannot connect to API"
```powershell
# Check if API is running
docker-compose ps api

# View API logs
docker-compose logs api

# Restart API
docker-compose restart api
```

### "Worker not processing tasks"
```powershell
# Check worker status
docker-compose ps worker

# View worker logs
docker-compose logs -f worker

# Restart worker
docker-compose restart worker
```

### "Database connection failed"
```powershell
# Check database status
docker-compose ps db

# Restart database
docker-compose restart db

# Reinitialize database
docker-compose exec api python init_db.py
```

### "Port already in use"
If ports 3000, 8000, 5432, or 6379 are in use:

```powershell
# Stop other services or change ports in docker-compose.yml
# For example, change "3000:3000" to "3001:3000"
```

## 📚 API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Key Endpoints

- `POST /api/auth/login` - Authenticate user
- `GET /api/events/` - List events (with filters)
- `POST /api/tasks/extract` - Queue URL extraction
- `GET /api/stats/` - Dashboard statistics
- `PUT /api/events/{id}` - Update event
- `POST /api/events/{id}/publish` - Publish to WordPress

## 🎨 Customization

### Styling
The frontend uses TailwindCSS. Customize colors in `web/tailwind.config.js`.

### Adding Extractors
Create new extractors in `worker/extractors/` following the pattern:

```python
def extract_custom(url):
    events = []
    # Your extraction logic
    return events
```

### Database Schema
Modify models in `api/models/` and create migrations.

## 🚢 Production Deployment

### Environment Variables
- Change `JWT_SECRET` to a strong random value
- Use production database credentials
- Enable HTTPS
- Set proper CORS origins

### Docker Production Build
```powershell
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling
- Run multiple worker instances
- Use managed PostgreSQL (AWS RDS, etc.)
- Use managed Redis (AWS ElastiCache, etc.)
- Deploy frontend to Vercel/Netlify
- Deploy API to AWS/GCP/Azure

## 📞 Support

- Check logs: `docker-compose logs -f`
- Review API docs: http://localhost:8000/docs
- Inspect database: `docker-compose exec db psql -U postgres events_cms`

## 🎉 Next Steps

1. **Test URL extraction** with real event URLs
2. **Customize the UI** to match your brand
3. **Set up WordPress integration** for publishing
4. **Add more extractors** for specific sources
5. **Deploy to production** when ready

Enjoy building your event aggregation platform! 🎊

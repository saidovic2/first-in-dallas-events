# Quick Start Guide

## Prerequisites

- **Docker Desktop** installed and running
- **Git** (optional, for version control)

## Setup (First Time)

1. Open PowerShell in this directory
2. Run the setup script:
   ```powershell
   .\setup.ps1
   ```

This will:
- Create environment configuration
- Build Docker containers
- Start all services (database, API, worker, web)
- Initialize database with sample data

## Starting the Application

```powershell
.\start.ps1
```

Or manually with Docker Compose:
```powershell
docker-compose up -d
```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Default Login

- **Email**: `admin@example.com`
- **Password**: `admin123`

## Stopping the Application

```powershell
.\stop.ps1
```

Or manually:
```powershell
docker-compose down
```

## Viewing Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f web
```

## Troubleshooting

### Port Already in Use

If you get port conflicts, stop other services using ports 3000, 8000, 5432, or 6379.

### Database Connection Issues

```powershell
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Frontend Not Loading

```powershell
# Rebuild and restart web container
docker-compose up -d --build web
```

### Worker Not Processing Tasks

```powershell
# Check worker logs
docker-compose logs -f worker

# Restart worker
docker-compose restart worker
```

## Development Mode

### Running API Locally (without Docker)

```powershell
cd api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

### Running Frontend Locally (without Docker)

```powershell
cd web
npm install
npm run dev
```

### Running Worker Locally (without Docker)

```powershell
cd worker
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python worker.py
```

## Features

### 1. Dashboard
- View analytics and statistics
- Monitor extraction tasks
- Track event status

### 2. Add Events
- Paste URLs to extract events
- Supports multiple sources:
  - Facebook Events
  - Instagram Posts
  - ICS/iCal files
  - RSS/Atom feeds
  - Webpages with JSON-LD
  - Generic webpages

### 3. Manage Events
- Review extracted events
- Edit event details
- Publish/unpublish events
- Push to WordPress (optional)
- Delete events

### 4. Public Directory
- Browse published events
- Filter by city, category, price
- Search events
- Grid and list views

## WordPress Integration (Optional)

To enable WordPress publishing:

1. Edit `.env` file:
   ```
   WP_BASE_URL=https://your-wordpress-site.com
   WP_USER=your-username
   WP_APP_PASSWORD=your-app-password
   ```

2. Restart services:
   ```powershell
   docker-compose restart api
   ```

## Sample Data

The system includes 6 sample events:
- Summer Music Festival 2024
- Tech Startup Networking Mixer
- Community Yoga in the Park
- Local Art Gallery Opening
- Food Truck Festival
- Charity Run for Education

## Next Steps

1. **Test URL Extraction**: Go to "Add Events" and paste a URL with event data
2. **Review Events**: Check "Manage Events" to see extracted events
3. **Customize**: Edit event details and publish
4. **Public View**: Visit the "Public Directory" to see how events appear to users

## Support

For issues or questions, check:
- API logs: `docker-compose logs api`
- Worker logs: `docker-compose logs worker`
- Database status: `docker-compose ps db`

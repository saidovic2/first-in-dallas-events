# 🎉 Local Event CMS

> **A production-ready SaaS platform for aggregating and managing local events**

Simply paste URLs (Facebook, Instagram, or any webpage) and automatically extract, manage, and publish event information.

---

## ✨ Features

- 🔍 **Smart Event Detection** - Automatically extracts event information from URLs
- 📊 **Analytics Dashboard** - Track events, extractions, and sources with real-time stats
- ✏️ **Event Management** - Review, edit, and publish events with full CRUD operations
- 🌐 **Public Directory** - Beautiful public-facing event listing with filters
- 🔄 **WordPress Integration** - One-click publishing to WordPress sites
- 🎨 **Modern UI** - Clean, responsive design with TailwindCSS and shadcn/ui
- 🚀 **Production Ready** - Docker orchestration, error handling, and comprehensive docs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │Add Events│  │  Manage  │  │ Public   │   │
│  │  /dash   │  │   /add   │  │ /events  │  │/directory│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │ HTTP/REST API
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼──────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   Auth   │  │  Events  │  │  Tasks   │  │  Stats   │    │
│  │  /auth   │  │ /events  │  │ /tasks   │  │ /stats   │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │
        ├─────────────┼─────────────┼─────────────┤
        │             │             │             │
┌───────▼─────────────▼─────────────▼─────────────▼───────────┐
│                    PostgreSQL Database                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Users   │  │  Events  │  │  Tasks   │  │ Sources  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└───────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
┌───────▼──────────┐                    ┌──────────▼──────────┐
│  Redis Queue     │                    │  Background Worker  │
│  (Task Queue)    │◄───────────────────┤  (Event Extractor)  │
└──────────────────┘                    │                     │
                                        │  ┌──────────────┐   │
                                        │  │  JSON-LD     │   │
                                        │  │  ICS Parser  │   │
                                        │  │  RSS Parser  │   │
                                        │  │  HTML Parser │   │
                                        │  └──────────────┘   │
                                        └─────────────────────┘
```

---

## 🚀 Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first CSS
- **shadcn/ui** - Beautiful UI components
- **Lucide React** - Icon library
- **Axios** - HTTP client

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **PostgreSQL** - Relational database
- **Redis** - Cache and task queue

### Worker
- **Playwright** - Browser automation
- **BeautifulSoup** - HTML parsing
- **ics** - Calendar file parsing
- **feedparser** - RSS/Atom parsing
- **python-dateutil** - Date parsing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FiD-Events-CMS
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker-compose up -d
```

4. Access the application:
   - **Frontend**: http://localhost:3000
   - **API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

### Default Admin Credentials

- **Email**: admin@example.com
- **Password**: admin123

## Project Structure

```
FiD-Events-CMS/
├── api/                 # FastAPI backend
│   ├── models/         # Database models
│   ├── routes/         # API endpoints
│   ├── schemas/        # Pydantic schemas
│   └── utils/          # Helper functions
├── worker/             # Background worker
│   ├── extractors/     # URL extraction logic
│   └── worker.py       # Main worker process
├── web/                # Next.js frontend
│   ├── app/            # App router pages
│   ├── components/     # React components
│   └── lib/            # Utilities
└── docker-compose.yml  # Docker orchestration
```

## Development

### Running Locally (without Docker)

#### Backend (API)
```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Worker
```bash
cd worker
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python worker.py
```

#### Frontend
```bash
cd web
npm install
npm run dev
```

## API Endpoints

- `POST /api/auth/login` - Admin login
- `POST /api/extract` - Queue URL extraction
- `GET /api/events` - List events with filters
- `PUT /api/events/{id}` - Update event
- `POST /api/events/{id}/publish` - Publish to WordPress
- `GET /api/stats` - Dashboard statistics
- `GET /api/tasks` - List extraction tasks

## Supported Event Sources

- JSON-LD structured data
- ICS/iCal files
- RSS/Atom feeds
- Facebook events
- Instagram posts
- Generic webpages with event metadata

## License

MIT

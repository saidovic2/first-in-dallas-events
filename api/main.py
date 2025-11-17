from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, events, tasks, stats, sync, ticketmaster, featured
from database import engine, Base

app = FastAPI(
    title="Local Event CMS API",
    description="API for managing and aggregating local events",
    version="1.0.0"
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://first-in-dallas.local",
        "https://first-in-dallas.local",
        "https://wonderful-vibrancy-production.up.railway.app",
        "*"  # Allow all origins in production (change to your domain when live)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(featured.router, prefix="/api/featured", tags=["Featured Events"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(sync.router, prefix="/api/sync", tags=["Bulk Sync"])
app.include_router(ticketmaster.router, prefix="/api/ticketmaster", tags=["Ticketmaster"])

@app.get("/")
async def root():
    return {
        "message": "Local Event CMS API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

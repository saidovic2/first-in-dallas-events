from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, events, tasks, stats, sync
from database import engine, Base

app = FastAPI(
    title="Local Event CMS API",
    description="API for managing and aggregating local events",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://first-in-dallas.local",
        "https://first-in-dallas.local"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(sync.router, prefix="/api/sync", tags=["Bulk Sync"])

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

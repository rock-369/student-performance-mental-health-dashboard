"""
Student Performance & Mental Health Dashboard API
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from routes import student_router, analytics_router, ml_router, auth_router, counseling_router, chat_router
from services import MLService
from database import engine, Base
import models.sql_models

# Create database tables (moved to lifespan)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Train ML models
    print("🚀 Starting up...")
    
    # Initialize DB with some data if needed (optional)
    
    # Startup
    print("🚀 Starting up...")
    models.sql_models.Base.metadata.create_all(bind=engine)
    print("🎉 API is ready!")
    
    yield  # Application runs here
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="AI-Powered Student Dashboard",
    description="Comprehensive Platform for Academic & Mental Health Analytics",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(analytics_router)
app.include_router(ml_router)
app.include_router(counseling_router)
app.include_router(chat_router)


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint - Health check"""
    return {
        "message": "Welcome to Student Performance & Mental Health Dashboard API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "students": "/students",
            "analytics": "/analytics",
            "ml": "/ml",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "Student Dashboard API"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

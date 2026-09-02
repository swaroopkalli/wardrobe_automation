import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
import app.models  # ensure models are registered with Base

from app.api.routes.wardrobe import router as wardrobe_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.legacy import router as legacy_router

# Auto-create tables if database is available
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    import logging
    logging.getLogger(__name__).warning("Could not auto-create database tables on startup (PostgreSQL offline or test environment): %s", e)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Modern Wardrobe Outfit Suggestion & Graph-based Recommendation API (FastAPI + PostgreSQL + Redis)"
)

# Enable CORS for frontend UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 Routers
app.include_router(wardrobe_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")

# Include root legacy routes for backward compatibility with frontend
app.include_router(legacy_router)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

"""
Main FastAPI application for Nomadly3 Clean Architecture
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import config
from app.core.security import secrets
from app.api.routes import user_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    
    # Validate configuration
    try:
        config.validate_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI application
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Clean Architecture Domain Registration Bot API",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(user_routes.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {config.APP_NAME} API",
        "version": config.APP_VERSION,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-07-23T07:30:00Z",
        "version": config.APP_VERSION
    }

@app.get("/config")
async def get_config():
    """Get application configuration (non-sensitive)"""
    return {
        "app_name": config.APP_NAME,
        "version": config.APP_VERSION,
        "debug": config.DEBUG,
        "default_language": config.DEFAULT_LANGUAGE,
        "offshore_multiplier": config.OFFSHORE_MULTIPLIER
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=config.DEBUG,
        log_level="info"
    )
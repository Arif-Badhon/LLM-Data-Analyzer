"""
Main FastAPI application entry point
Uses relative imports to work correctly from any directory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle"""
    # Startup
    logger.info("🚀 FastAPI application starting...")
    logger.info(f"Environment: {settings.fastapi_env}")
    yield
    # Shutdown
    logger.info("🛑 FastAPI application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="LLM Data Analyzer API",
    description="Backend API for LLM-based data analysis and ML suggestions",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.fastapi_env,
        "service": "llm-data-analyzer-backend"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "LLM Data Analyzer API",
        "version": "0.1.0",
        "docs_url": "/docs",
        "health_url": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.fastapi_env == "development"
    )

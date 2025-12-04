"""
FastAPI Application Entry Point
Supports MLX (local) and Docker Model Runner (containerized) modes
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.v1.router import router, init_services
from .services.llm_service import get_llm_service

logger = logging.getLogger(__name__)
logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # ===== STARTUP =====
    logger.info("🚀 FastAPI application starting...")
    logger.info(f"Environment: {settings.fastapi_env}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Get appropriate LLM service based on DEBUG flag
    logger.info("🚀 Initializing LLM service...")
    
    mlx_config = {
        "model_name": settings.llm_model_name_mlx,
        "max_tokens": settings.llm_max_tokens,
        "temperature": settings.llm_temperature,
        "device": settings.llm_device
    }
    
    docker_config = {
        "model_name": settings.llm_model_name_docker,
        "max_tokens": settings.llm_max_tokens,
        "temperature": settings.llm_temperature,
        "docker_url": settings.docker_model_runner_url,
        "timeout": settings.docker_timeout
    }
    
    llm_service = get_llm_service(
        debug=settings.debug,
        mlx_config=mlx_config,
        docker_config=docker_config
    )
    
    # Load model/initialize connection
    if await llm_service.load_model():
        logger.info("✅ LLM service ready")
    else:
        logger.warning("⚠️  LLM service initialization failed - will use fallback")
    
    # Pass llm_service to router module
    from .api.v1 import router as router_module
    router_module.llm_service = llm_service
    
    # Initialize other services
    logger.info("🚀 Initializing data services...")
    await init_services()
    logger.info("✅ All services initialized")
    
    yield
    
    # ===== SHUTDOWN =====
    logger.info("🛑 Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="LLM Data Analyzer",
    description="MLX LLM + Data Analysis Backend (Dual-mode: MLX or Docker Model Runner)",
    version="0.2.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)

logger.info("✅ FastAPI application configured")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "LLM Data Analyzer API",
        "version": "0.2.0",
        "docs_url": "/docs",
        "health_url": "/api/v1/health",
        "mode": "MLX (local)" if settings.debug else "Docker Model Runner"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.fastapi_env == "development"
    )

"""
Configuration for LLM Data Analyzer
Supports both MLX (local) and Docker Model Runner modes
All values from .env.local - NO hardcoded defaults
"""
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# Conditional MLX import
HAS_MLX = False

class Settings(BaseSettings):
    """Main settings - all from .env.local"""
    
    # ===== CORE SETTINGS =====
    fastapi_env: str
    fastapi_debug: bool
    log_level: str
    
    # ===== LLM MODE SELECTION =====
    # True = Use MLX locally (macOS Apple Silicon)
    # False = Use Docker Model Runner
    debug: bool
    
    # ===== MLX MODE (DEBUG=true) =====
    llm_model_name_mlx: str
    llm_max_tokens: int
    llm_temperature: float
    llm_device: str
    
    # ===== DOCKER MODEL RUNNER MODE (DEBUG=false) =====
    docker_model_runner_url: str
    llm_model_name_docker: str
    docker_timeout: int
    
    # ===== DATA PROCESSING =====
    max_file_size_mb: int
    
    # Hardcoded (lists can't be parsed from env vars)
    supported_file_types: list = ["csv", "xlsx", "xls"]
    
    class Config:
        env_file = ".env.local"
        case_sensitive = False

@lru_cache
def get_settings():
    """Get cached settings from .env.local"""
    return Settings()

# Check if MLX is available (only needed for DEBUG=true)
try:
    import mlx.core
    from mlx_lm import load
    from mlx_lm.generate import generate
    HAS_MLX = True
    logger.info("✅ MLX libraries available")
except ImportError:
    HAS_MLX = False
    logger.warning("⚠️  MLX not available (will use Docker Model Runner or mock)")

settings = get_settings()

# Export both settings and MLX availability
__all__ = ["settings", "get_settings", "HAS_MLX"]


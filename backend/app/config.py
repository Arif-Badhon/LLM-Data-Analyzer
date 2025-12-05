"""
Configuration for LLM Data Analyzer
Supports both MLX (local) and Docker Model Runner modes
All values from .env.local - NO hardcoded defaults
Follows Metis pattern for portability
"""
import logging
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


logger = logging.getLogger(__name__)


# Conditional MLX import
HAS_MLX = False


class Settings(BaseSettings):
    """Main settings - all from .env.local with sensible defaults"""
    
    # ===== CORE SETTINGS =====
    fastapi_env: str = Field(default="development", env="FASTAPI_ENV")
    fastapi_debug: bool = Field(default=False, env="FASTAPI_DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # ===== LLM MODE SELECTION =====
    # True = Use MLX locally (macOS Apple Silicon)
    # False = Use Docker Model Runner
    debug: bool = Field(default=False, env="DEBUG")
    llm_mode: str = Field(
        default="docker_model_runner",
        env="LLM_MODE",
        description="'mlx', 'docker_model_runner', or 'mock'"
    )
    
    # ===== MLX MODE (DEBUG=true) =====
    llm_model_name_mlx: str = Field(
        default="mlx-community/Llama-3.2-3B-Instruct-4bit",
        env="LLM_MODEL_NAME_MLX",
        description="MLX model from HuggingFace"
    )
    llm_max_tokens: int = Field(
        default=512,
        env="LLM_MAX_TOKENS",
        description="Max tokens for generation"
    )
    llm_temperature: float = Field(
        default=0.7,
        env="LLM_TEMPERATURE",
        description="Temperature for sampling (0.0-1.0)"
    )
    llm_device: str = Field(
        default="auto",
        env="LLM_DEVICE",
        description="MLX device: 'auto', 'cpu', 'gpu'"
    )
    
    # ===== DOCKER MODEL RUNNER MODE (DEBUG=false) =====
    # Metis pattern: stateless HTTP API to DMR on host
    runner_url: str = Field(
        default="http://host.docker.internal:11434/engines/llama.cpp/v1",
        env="MODEL_RUNNER_URL",
        description="Docker Model Runner API endpoint (from containers use host.docker.internal)"
    )
    llm_model: str = Field(
        default="ai/llama3.2:1B-Q4_0",
        env="MODEL_NAME",
        description="Model name as OCI reference (e.g., ai/llama3.2:1B-Q4_0)"
    )
    docker_timeout: int = Field(
        default=300,
        env="DOCKER_TIMEOUT",
        description="Timeout for Docker Model Runner requests (seconds)"
    )
    
    # ===== DATA PROCESSING =====
    max_file_size_mb: int = Field(
        default=50,
        env="MAX_FILE_SIZE_MB",
        description="Maximum file upload size in MB"
    )
    
    # Hardcoded (lists can't be parsed from env vars easily)
    supported_file_types: list = ["csv", "xlsx", "xls"]
    
    class Config:
        env_file = ".env.local"
        case_sensitive = False
        extra = "allow"
        # Fix Pydantic warning about protected namespaces
        protected_namespaces = ('settings_',)


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
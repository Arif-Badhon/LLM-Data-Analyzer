"""
Configuration management for FastAPI backend
Loads ALL settings from .env.local at project ROOT
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import logging


def find_env_file() -> Path:
    """Find .env.local by checking multiple paths"""
    possible_paths = [
        Path("/Users/arif/Projects/Personal/LLM-Data-Analyzer/.env.local"),
        Path.cwd() / ".env.local",
        Path(__file__).parent.parent.parent / ".env.local",
        Path(__file__).parent.parent / ".env.local",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError(
        f"❌ .env.local not found! Checked:\n" + 
        "\n".join([f"  - {p}" for p in possible_paths])
    )


class Settings(BaseSettings):
    """Application settings - ALL loaded from .env.local"""
    
    # API Configuration
    fastapi_env: str
    api_host: str
    api_port: int
    log_level: str
    
    # LLM Configuration
    llm_model_name: str
    llm_max_tokens: int
    llm_temperature: float
    llm_device: str
    
    # File Upload
    max_file_size: int
    upload_timeout: int
    
    # CORS
    cors_origins: List[str]
    
    class Config:
        env_file = str(find_env_file())
        case_sensitive = False
        extra = "ignore"


settings = Settings()


def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(settings.log_level)
    return logger

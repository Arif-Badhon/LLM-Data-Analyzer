"""LLM Service - handles MLX Llama 2 inference"""
from app.config import get_logger

logger = get_logger(__name__)

class LLMService:
    """Wrapper around MLX LLM for convenient inference"""
    
    def __init__(self):
        """Initialize LLM Service - actual LLM loading in Phase 2"""
        self.llm = None
        logger.info("LLMService initialized (Phase 2 will load actual model)")
    
    async def chat(self, message: str, history: list = None) -> str:
        """Process user message and return LLM response"""
        logger.info(f"Chat request: {message}")
        return "LLM response will be here in Phase 2"

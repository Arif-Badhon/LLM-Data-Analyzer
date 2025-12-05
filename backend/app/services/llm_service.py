"""
Dual-mode LLM Service
- DEBUG=true: Uses MLX with Apple Silicon GPU
- DEBUG=false: Uses Docker Model Runner (OpenAI-compatible API)
- Fallback: Mock mode if neither available
"""
import asyncio
import logging
import os
from abc import ABC, abstractmethod
from typing import List, Optional
import httpx


logger = logging.getLogger(__name__)


# Import MLX conditionally
try:
    from mlx_lm import load
    from mlx_lm.generate import generate
    HAS_MLX = True
except ImportError:
    HAS_MLX = False



class BaseLLMService(ABC):
    """Abstract base class for LLM services"""
    
    def __init__(self, model_name: str, max_tokens: int, temperature: float):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.is_loaded = False
        self.is_mock = False
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    async def load_model(self) -> bool:
        """Load/initialize the model"""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate text from prompt"""
        pass
    
    async def chat(self, messages: List[dict], system_prompt: str = None) -> str:
        """Chat interface - converts chat format to prompt format"""
        prompt = self._build_prompt(messages, system_prompt)
        return await self.generate(prompt)
    
    def _build_prompt(self, messages: List[dict], system_prompt: str = None) -> str:
        """Build prompt from chat messages"""
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}\n\n")
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.capitalize()}: {content}\n")
        
        prompt_parts.append("Assistant: ")
        return "".join(prompt_parts)



class LLMServiceMLX(BaseLLMService):
    """MLX implementation for Apple Silicon (DEBUG=true)"""
    
    def __init__(self, model_name: str, max_tokens: int, temperature: float, device: str):
        super().__init__(model_name, max_tokens, temperature)
        self.device = device
        self.model = None
        self.tokenizer = None
    
    async def load_model(self) -> bool:
        """Load MLX model"""
        if self.is_loaded:
            return True
        
        if not HAS_MLX:
            self.logger.error("❌ MLX not available")
            return False
        
        try:
            self.logger.info(f"🔄 Loading MLX model: {self.model_name}")
            loop = asyncio.get_event_loop()
            self.model, self.tokenizer = await loop.run_in_executor(
                None,
                self._load_model_sync
            )
            self.is_loaded = True
            self.logger.info(f"✅ MLX model loaded: {self.model_name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ MLX model loading failed: {e}")
            return False
    
    def _load_model_sync(self):
        """Synchronous MLX model loading"""
        if not HAS_MLX:
            raise RuntimeError("MLX not installed")
        
        self.logger.info("🔄 Starting model download/load...")
        model, tokenizer = load(self.model_name)
        self.logger.info("✅ Model download/load complete")
        return model, tokenizer
    
    async def generate(self, prompt: str) -> str:
        """Generate with MLX"""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._generate_sync,
                prompt
            )
            return response
        except Exception as e:
            self.logger.error(f"❌ MLX generation failed: {e}")
            raise
    
    def _generate_sync(self, prompt: str) -> str:
        """Synchronous text generation with MLX"""
        response = generate(
            model=self.model,
            tokenizer=self.tokenizer,
            prompt=prompt,
            max_tokens=self.max_tokens
        )
        return response




class LLMServiceDockerModelRunner(BaseLLMService):
    """Docker Model Runner implementation - OpenAI-compatible API
    
    Uses stateless HTTP calls to DMR running on host machine.
    Optimal for Apple Silicon GPU acceleration via llama.cpp Metal backend.
    """
    
    def __init__(
        self, 
        model_name: str, 
        max_tokens: int, 
        temperature: float, 
        docker_url: str,
        timeout: int = 300
    ):
        super().__init__(model_name, max_tokens, temperature)
        self.docker_url = docker_url.rstrip("/")  # Remove trailing slash
        self.timeout = timeout
        self.client = None
    
    async def load_model(self) -> bool:
        """Initialize Docker Model Runner connection
        
        Tests connectivity to the DMR HTTP API endpoint.
        DMR itself handles model loading on the host.
        """
        if self.is_loaded:
            return True
        
        try:
            self.logger.info(f"🔄 Connecting to Docker Model Runner: {self.docker_url}")
            self.client = httpx.AsyncClient(timeout=self.timeout)
            
            # OpenAI-compatible endpoint: GET /v1/models
            response = await self.client.get(f"{self.docker_url}/models")
            
            if response.status_code == 200:
                models = response.json()
                self.logger.info(f"✅ Docker Model Runner connected")
                self.logger.info(f"📋 Available models: {models}")
                self.is_loaded = True
                return True
            else:
                self.logger.error(f"❌ Docker Model Runner returned {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Docker Model Runner connection failed: {e}")
            return False
    
    async def generate(self, prompt: str) -> str:
        """Generate with Docker Model Runner (OpenAI-compatible API)
        
        Makes HTTP request to DMR at host.docker.internal:11434
        Model inference happens on host GPU (Apple Metal backend)
        """
        if not self.is_loaded:
            raise RuntimeError("Docker Model Runner not connected")
        
        try:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            
            # OpenAI-compatible endpoint: POST /v1/chat/completions
            response = await self.client.post(
                f"{self.docker_url}/chat/completions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                self.logger.error(f"❌ Docker Model Runner error: {response.status_code} - {response.text}")
                raise RuntimeError(f"Model Runner error: {response.status_code}")
        except Exception as e:
            self.logger.error(f"❌ Docker Model Runner generation failed: {e}")
            raise
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()




class LLMServiceMock(BaseLLMService):
    """Mock implementation as fallback"""
    
    def __init__(self, model_name: str, max_tokens: int, temperature: float):
        super().__init__(model_name, max_tokens, temperature)
        self.is_mock = True
    
    async def load_model(self) -> bool:
        """Mock loading"""
        self.logger.warning("⚠️  Using MOCK mode (no real LLM available)")
        self.is_loaded = True
        return True
    
    async def generate(self, prompt: str) -> str:
        """Generate mock response"""
        return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate intelligent mock responses"""
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm running in mock mode (no LLM available). I can still help you analyze CSV and Excel files!"
        elif "analyze" in prompt_lower or "data" in prompt_lower:
            return "I can analyze your data with statistical analysis, trend detection, outlier detection, and correlation matrices."
        elif "what can" in prompt_lower or "help" in prompt_lower:
            return "I can help with: 1) Chatting, 2) Uploading files (CSV/Excel), 3) Statistical analysis, 4) Trend detection, 5) Anomaly detection."
        elif "machine learning" in prompt_lower:
            return "Machine learning is about creating algorithms that can learn from data and make predictions without being explicitly programmed."
        else:
            return f"Mock response: I processed your prompt about '{prompt[:40]}...' - please note I'm in mock mode with no real LLM."



def get_llm_service(debug: bool = None, mlx_config: dict = None, docker_config: dict = None, settings=None) -> BaseLLMService:
    """
    Factory function to get appropriate LLM service
    
    Fallback chain: MLX (DEBUG=true) → Docker Model Runner → Mock
    
    Args:
        debug: Force DEBUG mode (True=MLX, False=Docker). If None, reads from env/settings
        mlx_config: Manual MLX config dict
        docker_config: Manual Docker config dict
        settings: Pydantic Settings object with llm config
    
    Returns:
        BaseLLMService: One of MLX, DockerModelRunner, or Mock implementation
    """
    
    # Determine debug mode
    if debug is None:
        debug = os.getenv("DEBUG", "false").lower() == "true"
        if hasattr(settings, "debug"):
            debug = settings.debug
    
    # Try MLX first (if DEBUG=true)
    if debug and HAS_MLX:
        try:
            config = mlx_config or {
                "model_name": "mlx-community/Llama-3.2-3B-Instruct-4bit",
                "max_tokens": 512,
                "temperature": 0.7,
                "device": "auto"
            }
            logger.info("📌 Mode: MLX (DEBUG=true) with Apple Silicon GPU")
            return LLMServiceMLX(**config)
        except Exception as e:
            logger.warning(f"⚠️  MLX failed: {e}, falling back to Docker Model Runner")
    
    # Try Docker Model Runner (Metis pattern)
    docker_url = None
    if docker_config:
        docker_url = docker_config.get("docker_url")
    elif settings:
        docker_url = getattr(settings, "model_runner_url", None)
    else:
        docker_url = os.getenv("MODEL_RUNNER_URL")
    
    if docker_url:
        try:
            model_name = None
            if docker_config:
                model_name = docker_config.get("model_name")
            elif settings:
                model_name = getattr(settings, "model_name", None)
            else:
                model_name = os.getenv("MODEL_NAME", "llama3.2:1B-Q4_0")
            
            config = {
                "model_name": model_name,
                "max_tokens": (docker_config or {}).get("max_tokens", 
                    getattr(settings, "llm_max_tokens", 512) if settings else 512),
                "temperature": (docker_config or {}).get("temperature", 
                    getattr(settings, "llm_temperature", 0.7) if settings else 0.7),
                "docker_url": docker_url,
                "timeout": (docker_config or {}).get("timeout", 
                    getattr(settings, "docker_timeout", 300) if settings else 300)
            }
            logger.info(f"📌 Mode: Docker Model Runner at {docker_url}")
            logger.info(f"📌 Model: {config['model_name']}")
            logger.info(f"✅ Using host GPU acceleration (llama.cpp Metal backend)")
            return LLMServiceDockerModelRunner(**config)
        except Exception as e:
            logger.warning(f"⚠️  Docker Model Runner failed: {e}, falling back to Mock")
    
    # Fallback to mock
    logger.warning("⚠️  Using MOCK mode (no LLM available)")
    return LLMServiceMock(
        model_name="mock",
        max_tokens=512,
        temperature=0.7
    )
"""API client for backend communication"""
import requests
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Import config
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE_URL = f"{BACKEND_URL}/api/v1"
TIMEOUT_LONG = 120


class APIClient:
    """Client for backend API communication"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.timeout = TIMEOUT_LONG
    
    def health_check(self) -> Dict[str, Any]:
        """Check backend health status"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {"status": "error", "detail": str(e)}
    
    def chat(self, messages: List[Dict], system_prompt: str = None) -> Dict[str, Any]:
        """Send chat request to backend"""
        try:
            payload = {
                "messages": messages,
                "system_prompt": system_prompt or "You are a helpful data analysis assistant."
            }
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Chat request failed: {e}")
            return {"error": str(e)}
    
    def upload_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Upload file to backend"""
        try:
            files = {"file": (filename, file_bytes)}
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ File upload failed: {e}")
            return {"error": str(e)}
    
    def analyze(self, data: List[Dict], analysis_type: str, columns: List[str] = None) -> Dict[str, Any]:
        """Request data analysis"""
        try:
            payload = {
                "data": data,
                "analysis_type": analysis_type,
                "columns": columns or []
            }
            response = requests.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Analysis request failed: {e}")
            return {"error": str(e)}
    
    def get_suggestions(self, data: List[Dict], context: str = None) -> Dict[str, Any]:
        """Get AI suggestions for data"""
        try:
            payload = {
                "data": data,
                "analysis_context": context or ""
            }
            response = requests.post(
                f"{self.base_url}/suggestions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Suggestion request failed: {e}")
            return {"error": str(e)}


# Global client instance
client = APIClient()

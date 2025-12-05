"""Configuration for frontend"""
import os
from dotenv import load_dotenv

load_dotenv()

# Backend API
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE_URL = f"{BACKEND_URL}/api/v1"

# Timeouts
TIMEOUT_SHORT = 5
TIMEOUT_LONG = 120

# UI Settings
PAGE_TITLE = "LLM Data Analyzer"
PAGE_ICON = "🤖"

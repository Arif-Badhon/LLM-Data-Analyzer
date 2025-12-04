"""
API v1 Router - Main entry point for all endpoints
Supports dual-mode LLM (MLX or Docker Model Runner)
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Optional
from datetime import datetime
import logging

from ...models.schemas import (
    ChatRequest, ChatResponse,
    FileUploadResponse, AnalysisRequest, AnalysisResponse,
    SuggestionRequest, SuggestionsResponse, HealthResponse
)
from ...services.data_processor import DataProcessor
from ...services.analyzer import Analyzer
from ...services.ml_suggester import MLSuggester
from ...config import settings

router = APIRouter(prefix="/api/v1", tags=["v1"])
logger = logging.getLogger(__name__)

# Global service instances
llm_service = None  # Will be set from main.py
data_processor: Optional[DataProcessor] = None
analyzer: Optional[Analyzer] = None
ml_suggester: Optional[MLSuggester] = None


async def init_services():
    """Initialize all services on startup (except LLM - done in main.py)"""
    global data_processor, analyzer, ml_suggester
    
    logger.info("🚀 Initializing data services...")
    
    data_processor = DataProcessor()
    analyzer = Analyzer()
    ml_suggester = MLSuggester()
    
    logger.info("✅ Data services initialized")


# ============ Chat Endpoint ============

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with LLM about data analysis"""
    if not llm_service or not llm_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="LLM not ready - still loading or connection failed"
        )
    
    try:
        logger.info(f"💬 Chat request with {len(request.messages)} messages")
        
        # Convert Pydantic ChatMessage objects to dictionaries
        messages_dict = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        response = await llm_service.chat(
            messages_dict,
            request.system_prompt
        )
        
        # Determine which model name to return based on DEBUG mode
        model_name = (
            settings.llm_model_name_mlx if settings.debug
            else settings.llm_model_name_docker
        )
        
        return ChatResponse(
            response=response,
            model=model_name
        )
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ File Upload Endpoint ============

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process data file (CSV or Excel)"""
    try:
        if not data_processor:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        logger.info(f"📁 Processing file: {file.filename}")
        data, file_type = await data_processor.process_file(file)
        
        # Get preview (first 5 rows)
        preview = data[:5] if data else []
        
        # Get column names
        column_names = list(data.keys()) if data else []
        
        return FileUploadResponse(
            filename=file.filename,
            size=len(str(data)),
            rows=len(data),
            columns=len(column_names),
            column_names=column_names,
            preview=preview,
            file_type=file_type
        )
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Analysis Endpoint ============

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    """Analyze data - supports multiple analysis types"""
    try:
        if not analyzer:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        logger.info(f"📊 Analysis: {request.analysis_type} on {len(request.data)} rows")
        
        results = analyzer.analyze(
            request.data,
            request.analysis_type,
            request.columns
        )
        
        summary = analyzer.generate_summary(results)
        
        return AnalysisResponse(
            analysis_type=request.analysis_type,
            results=results,
            summary=summary,
            timestamp=datetime.now()
        )
    except ValueError as e:
        logger.error(f"Invalid analysis request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ML Suggestions Endpoint ============

@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(request: SuggestionRequest):
    """Get ML-based suggestions for data improvement"""
    try:
        if not ml_suggester:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        logger.info(f"🤖 Generating suggestions for {len(request.data)} rows")
        
        suggestions_list = ml_suggester.generate(
            request.data,
            request.analysis_context
        )
        
        return SuggestionsResponse(
            suggestions=suggestions_list,
            total_suggestions=len(suggestions_list),
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"❌ Suggestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Health Check ============

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - shows current LLM mode"""
    
    # Determine LLM status
    llm_status = "unknown"
    if llm_service:
        if llm_service.is_mock:
            llm_status = "mock-mode"
        elif llm_service.is_loaded:
            llm_status = "loaded"
        else:
            llm_status = "failed"
    
    # Show which mode is active
    mode = "MLX (local)" if settings.debug else "Docker Model Runner"
    
    return HealthResponse(
        status="healthy",
        environment=settings.fastapi_env,
        service="llm-data-analyzer-backend",
        llm_loaded=llm_service.is_loaded if llm_service else False,
        llm_model=(
            settings.llm_model_name_mlx if settings.debug
            else settings.llm_model_name_docker
        ),
        version="0.2.0"
    )

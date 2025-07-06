import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# from app.services.mock_gpt_service import analyze_logs
from app.services.gpt_service import analyze_logs
from app.core.logger import log_analysis_request, log_error, logger

router = APIRouter()

class LogRequest(BaseModel):
    log: str

@router.post("/analyze")
async def analyze_log(request: LogRequest):
    start_time = time.time()
    
    if not request.log.strip():
        logger.warning("Empty log submitted for analysis")
        raise HTTPException(status_code=400, detail="Log cannot be empty.")
    
    try:
        logger.info(f"Starting analysis of log with {len(request.log)} characters")
        
        result = analyze_logs(request.log)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log successful analysis
        log_analysis_request(
            log_length=len(request.log),
            analysis_duration=duration,
            log_preview=request.log[:100] + "..." if len(request.log) > 100 else request.log
        )
        
        logger.info("Analysis completed successfully")
        return {"analysis": result, "metadata": {"log_length": len(request.log), "processing_time_ms": round(duration * 1000, 2)}}
        
    except Exception as e:
        duration = time.time() - start_time
        log_error(
            error=e,
            context="Log analysis",
            log_length=len(request.log),
            duration=duration
        )
        raise HTTPException(status_code=500, detail=str(e))

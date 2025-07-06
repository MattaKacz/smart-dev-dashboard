"""
Prometheus metrics endpoint
"""
from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
from app.services.metrics_service import metrics_service
from app.core.logger import logger

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    """Expose Prometheus metrics"""
    try:
        metrics = metrics_service.get_metrics()
        return PlainTextResponse(metrics, media_type="text/plain")
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return PlainTextResponse("", status_code=500) 
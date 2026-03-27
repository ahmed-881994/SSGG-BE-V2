from fastapi import APIRouter, Depends, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST

# from app.core.dependencies import get_user_in_token
from app.services.metrics_service import MetricsService

router = APIRouter(tags=["Metrics"], include_in_schema=False)

@router.get("/metrics")
async def health_check():
    """Metrics endpoint for monitoring"""
    metrics_service = MetricsService()
    
    metrics = metrics_service.get_application_metrics()
    return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)
from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_user_in_token
from app.services.healthcheck_service import HealthCheckService

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    """Comprehensive health check"""
    health_service = HealthCheckService()
    health_status = health_service.check_health(summary_only=True)

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/health/report")
def health_report(current_user=Depends(get_user_in_token)):
    """Health report"""
    health_service = HealthCheckService()
    health_report = health_service.check_health()
    if health_report["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_report)
    return health_report
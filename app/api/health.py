from fastapi import APIRouter, HTTPException
from app.service.health.health_check import check_application_health

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    """Comprehensive health check"""
    health_status = check_application_health()
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status
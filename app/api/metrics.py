from fastapi import APIRouter, Depends, HTTPException

# from app.core.dependencies import get_user_in_token
# from app.services.healthcheck_service import HealthCheckService

router = APIRouter(tags=["Metrics"], include_in_schema=False)

@router.get("/metrics")
async def health_check():
    """Metrics endpoint for monitoring"""
    pass
    # health_service = HealthCheckService()
    # health_status = await health_service.check_health(summary_only=True)

    # if health_status["status"] == "unhealthy":
    #     raise HTTPException(status_code=503, detail=health_status)
    
    # return health_status

# @router.get("/health/report")
# async def health_report(current_user=Depends(get_user_in_token)):
#     """Health report"""
#     health_service = HealthCheckService()
#     health_report = await health_service.check_health()
#     if health_report["status"] == "unhealthy":
#         raise HTTPException(status_code=503, detail=health_report)
#     return health_report
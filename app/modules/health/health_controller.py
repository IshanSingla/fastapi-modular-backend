from fastapi import APIRouter, Depends, Request
from .health_service import get_health_status
from .health_constants import STATUS_OK, MSG_HEALTH_OK, MSG_HEALTH_FAIL
from app.core.logger import setup_logging
from app.core.response import ResponseModel
from app.core.tracing import trace_request

logger = setup_logging()
router = APIRouter()

@router.get("/")
async def health_check(request: Request, response: ResponseModel = Depends(trace_request)):
    """
    Perform a health check of the service
    
    Returns:
        dict: Health status information
    """
    logger.info(f"Health check requested - Trace ID: {response.trace_id}")
    health_data = await get_health_status()
    
    return response.success_response(
        data= health_data["components"],
        message=MSG_HEALTH_OK if health_data["status"] == STATUS_OK else MSG_HEALTH_FAIL
    )

@router.get("/readiness")
async def readiness_check(response: ResponseModel = Depends(trace_request)):
    """
    Check if the service is ready to accept requests
    
    Returns:
        dict: Readiness status information
    """
    logger.info(f"Readiness check requested - Trace ID: {response.trace_id}")
    return response.success_response(
        data="ready",
        message="Service is ready to accept requests"
    )

@router.get("/liveness")
async def liveness_check(response: ResponseModel = Depends(trace_request)):
    """
    Check if the service is alive
    
    Returns:
        dict: Liveness status information
    """
    logger.info(f"Liveness check requested - Trace ID: {response.trace_id}")
    return response.success_response(
        data="alive",
        message="Service is alive"
    )


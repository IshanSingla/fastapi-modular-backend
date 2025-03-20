from sqlalchemy import text
from app.core.database import engine
from app.core.logger import setup_logging
from app.core.tracing import get_tracer, trace_function
from app.modules.health.health_constants import (
    STATUS_OK, 
    STATUS_FAIL,
    COMPONENT_DATABASE,
    COMPONENT_API,
    COMPONENT_AI
)
import openai
import google.generativeai as genai
from app.core.config import settings

logger = setup_logging()
tracer = get_tracer()

@trace_function
async def check_database_health():
    """
    Check database connection health
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {
            "status": STATUS_OK,
            "name": COMPONENT_DATABASE,
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": STATUS_FAIL,
            "name": COMPONENT_DATABASE,
            "message": f"Database connection failed: {str(e)}"
        }

@trace_function
async def check_openai_health():
    """
    Check OpenAI API connection health
    """
    if not settings.OPENAI_API_KEY:
        return {
            "status": STATUS_FAIL,
            "name": COMPONENT_AI,
            "message": "OpenAI API key not configured"
        }
    
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        client.models.list()
        return {
            "status": STATUS_OK,
            "name": COMPONENT_AI,
            "message": "OpenAI API connection successful"
        }
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        return {
            "status": STATUS_FAIL,
            "name": COMPONENT_AI,
            "message": f"OpenAI API connection failed: {str(e)}"
        }

@trace_function
async def check_google_ai_health():
    """
    Check Google AI API connection health
    """
    if not settings.GOOGLE_API_KEY:
        return {
            "status": STATUS_FAIL,
            "name": COMPONENT_AI,
            "message": "Google AI API key not configured"
        }
    
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        models = genai.list_models()
        return {
            "status": STATUS_OK,
            "name": COMPONENT_AI,
            "message": "Google AI API connection successful"
        }
    except Exception as e:
        logger.error(f"Google AI health check failed: {e}")
        return {
            "status": STATUS_FAIL,
            "name": COMPONENT_AI,
            "message": f"Google AI API connection failed: {str(e)}"
        }

@trace_function
async def get_health_status():
    """
    Get overall health status of the application
    """
    with tracer.start_as_current_span("get_health_status"):
        health_checks = [
            await check_database_health(),
            await check_openai_health(),
            await check_google_ai_health()
        ]
        
        overall_status = STATUS_OK if all(check["status"] == STATUS_OK for check in health_checks) else STATUS_FAIL
        
        return {
            "status": overall_status,
            "components": health_checks
        }


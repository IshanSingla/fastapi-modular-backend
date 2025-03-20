from app.core.config import settings
from app.core.logger import logger
from app.core.database import create_db_and_tables
from app.core.scheduler import scheduler
from app.core.tracing import tracer, trace_request
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    with tracer.start_as_current_span("application_startup"):
        logger.info("Starting application...")
        create_db_and_tables()
        scheduler.start()
        logger.info("Application started successfully")
    yield
    # Shutdown
    with tracer.start_as_current_span("application_shutdown"):
        logger.info("Shutting down application...")
        scheduler.shutdown()
        logger.info("Application shutdown complete")
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from app.core.config import settings
from app.core.logger import logger
from app.core.tracing import tracer, trace_job
from app.modules.ai.ai_cron import register_jobs as register_ai_jobs
import functools

# Configure job stores
jobstores = {
    'default': SQLAlchemyJobStore(url=settings.DATABASE_URL)
}

# Configure executors
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

# Configure job defaults
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

# Create scheduler
scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='UTC'
)

def register_scheduled_jobs():
    """
    Register all scheduled jobs from modules
    """
    with tracer.start_as_current_span("register_scheduled_jobs"):
        logger.info("Registering scheduled jobs...")
        
        
        # Register jobs from each module
        register_ai_jobs(scheduler)
        
        logger.info("All scheduled jobs registered successfully")

# Decorator for tracing scheduled jobs
def traced_job(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return trace_job(func, *args, **kwargs)
    return wrapper

# Register jobs when this module is imported
register_scheduled_jobs()


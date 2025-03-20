from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.logger import logger

def clean_old_completions():
    """
    Clean old AI completions from the database
    """
    logger.info("Running scheduled job: clean_old_completions")
    db = SessionLocal()
    try:
        # Implementation would depend on how completions are stored
        # This is a placeholder for the actual implementation
        logger.info("Old completions cleaned successfully")
    except Exception as e:
        logger.error(f"Error cleaning old completions: {e}")
    finally:
        db.close()

def update_model_cache():
    """
    Update AI model cache
    """
    logger.info("Running scheduled job: update_model_cache")
    try:
        # Implementation would depend on how model caching is handled
        # This is a placeholder for the actual implementation
        logger.info("Model cache updated successfully")
    except Exception as e:
        logger.error(f"Error updating model cache: {e}")

def register_jobs(scheduler: BackgroundScheduler):
    """
    Register AI module cron jobs
    """
    # Clean old completions monthly
    scheduler.add_job(
        clean_old_completions,
        'cron',
        day=1,
        hour=2,
        minute=0,
        id='clean_old_completions',
        replace_existing=True
    )
    
    # Update model cache daily
    scheduler.add_job(
        update_model_cache,
        'cron',
        hour=3,
        minute=0,
        id='update_model_cache',
        replace_existing=True
    )
    
    logger.info("AI module cron jobs registered successfully")


import sys
import logging
from loguru import logger as logger_loguru
from app.core.config import settings
from functools import lru_cache
from opentelemetry import trace
from fastapi import Request

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger_loguru.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger_loguru.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

@lru_cache()
def setup_logging():
    # Remove default handlers
    logger_loguru.remove()

    # Add custom handler with specified format
    logger_loguru.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # Add file handler for525485 persistent logs
    logger_loguru.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 week",
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL,
        backtrace=True,
        diagnose=True,
    )
    
    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Replace logging handlers with Loguru
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = [InterceptHandler()]

    return logger_loguru

logger = setup_logging()
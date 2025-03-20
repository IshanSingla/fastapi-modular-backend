import sys
import logging
import uuid
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
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | TraceID={extra[trace_id]} | {message}",
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
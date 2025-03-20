from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Modular FastAPI Backend"
    PROJECT_DESCRIPTION: str = "A modular FastAPI backend with various integrations"
    PROJECT_VERSION: str = "0.1.0"
    
    # API settings
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Google AI settings
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # AWS S3 settings
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "{time} | {level} | {message}"
    
    # Tracing settings
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "True").lower() == "true"
    OTLP_ENDPOINT: Optional[str] = os.getenv("OTLP_ENDPOINT")

    PORT: int = os.getenv("PORT", 8000)

    ENV:str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()


from pydantic import BaseModel
from typing import Any, Optional, Dict, TypeVar, Generic
from fastapi.responses import JSONResponse

T = TypeVar('T')

class MetaData(BaseModel):
    """
    Metadata for API responses
    """
    traceId: str
    isSuccess: bool
    message: str
    error: Optional[str] = None

class ResponseModel:
    """
    Standard response model for API endpoints
    """
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
    
    def success_response(self, data: Any, message: str = "Success"):
        """
        Create a success response
        """
        return {
            "data": data,
            "meta": {
                "traceId": self.trace_id,
                "isSuccess": True,
                "message": message,
                "error": None
            }
        }
    
    def error_response(self, message: str, error: str = None, status_code: int = 400):
        """
        Create an error response
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "data": None,
                "meta": {
                    "traceId": self.trace_id,
                    "isSuccess": False,
                    "message": message,
                    "error": error
                }
            }
        )

def create_response(data: Any, trace_id: str, is_success: bool, message: str, error: str = None):
    """
    Create a standardized response
    """
    return {
        "data": data,
        "meta": {
            "traceId": trace_id,
            "isSuccess": is_success,
            "message": message,
            "error": error
        }
    }

class StandardResponse(Generic[T], BaseModel):
    """
    Pydantic model for standardized API responses
    """
    data: Optional[T] = None
    meta: MetaData
    
    class Config:
        arbitrary_types_allowed = True


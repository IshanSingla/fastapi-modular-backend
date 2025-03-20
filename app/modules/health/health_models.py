from pydantic import BaseModel
from typing import List, Optional

class ComponentHealth(BaseModel):
    """
    Health status of a component
    """
    status: str
    name: str
    message: str

class HealthStatus(BaseModel):
    """
    Overall health status of the application
    """
    status: str
    components: List[ComponentHealth]

class ReadinessStatus(BaseModel):
    """
    Readiness status of the application
    """
    status: str

class LivenessStatus(BaseModel):
    """
    Liveness status of the application
    """
    status: str


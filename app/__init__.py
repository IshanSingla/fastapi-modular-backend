from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid

from app.core.config import settings
from app.core.logger import logger
from app.core.database import create_db_and_tables
from app.core.lifespan import lifespan
from app.modules.health.health_controller import router as health_router
from app.core.tracing import tracer, trace_request
from app.core.response import ResponseModel, create_response

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response interceptor middleware
@app.middleware("http")
async def response_interceptor(request: Request, call_next):
    # Generate trace ID for the request
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id
    
    # Add trace context to the request
    with tracer.start_as_current_span(
        f"{request.method} {request.url.path}",
        attributes={
            "http.method": request.method,
            "http.url": str(request.url),
            "trace_id": trace_id
        }
    ) as span:
        try:
            # Process the request
            response = await call_next(request)
            
            # If the response is already a JSONResponse, we need to modify its content
            if isinstance(response, JSONResponse):
                content = response.body.decode()
                
                # Only intercept JSON responses that aren't already in our format
                if content and "meta" not in content:
                    import json
                    data = json.loads(content)
                    
                    # Create standardized response
                    new_content = create_response(
                        data=data,
                        trace_id=trace_id,
                        is_success=True,
                        message="Success"
                    )
                    
                    return JSONResponse(
                        content=new_content,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
            
            return response
        except Exception as e:
            logger.exception(f"Error processing request: {e}")
            span.record_exception(e)
            
            # Create error response
            error_response = create_response(
                data=None,
                trace_id=trace_id,
                is_success=False,
                message="Internal Server Error",
                error=str(e)
            )
            
            return JSONResponse(
                content=error_response,
                status_code=500
            )

# Include routers
app.include_router(health_router, prefix="/api/health", tags=["Health"])

@app.get("/", tags=["Root"])
async def root(response: ResponseModel = Depends(trace_request)):
    return response.success_response(
        data={"message": f"Welcome to {settings.PROJECT_NAME} API"},
        message="API is running"
    )
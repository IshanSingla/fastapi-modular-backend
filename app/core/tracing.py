import functools
import uuid
from fastapi import Request, Depends
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from app.core.config import settings
from app.core.response import ResponseModel
from functools import lru_cache

# Initialize tracer
def initialize_tracer():
    """
    Initialize OpenTelemetry tracer
    """
    if not settings.ENABLE_TRACING:
        # Return a no-op tracer if tracing is disabled
        return trace.get_tracer(__name__)
    
    # Create a resource with service name
    resource = Resource(attributes={
        SERVICE_NAME: settings.PROJECT_NAME
    })
    
    # Create a tracer provider
    provider = TracerProvider(resource=resource)
    
    # If OTLP endpoint is configured, use it
    if settings.OTLP_ENDPOINT:
        otlp_exporter = OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Set the global tracer provider
    trace.set_tracer_provider(provider)
    
    # Get a tracer
    return trace.get_tracer(__name__)

# Get tracer instance
@lru_cache()
def get_tracer():
    """
    Get the tracer instance
    """
    return initialize_tracer()

# Trace a function
def trace_function(func, span_name=None):
    """
    Trace a function execution
    """
    tracer = get_tracer()
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = span_name or f"{func.__module__}.{func.__name__}"
        with tracer.start_as_current_span(name) as span:
            # Add function arguments as span attributes
            span.set_attribute("function.name", func.__name__)
            span.set_attribute("function.module", func.__module__)
            
            # Execute the function
            return func(*args, **kwargs)
    
    return wrapper

# Trace a job
def trace_job(func, *args, **kwargs):
    """
    Trace a scheduled job execution
    """
    tracer = get_tracer()
    trace_id = str(uuid.uuid4())
    
    with tracer.start_as_current_span(
        f"job.{func.__name__}",
        attributes={
            "job.name": func.__name__,
            "job.trace_id": trace_id
        }
    ) as span:
        try:
            result = func(*args, **kwargs)
            span.set_attribute("job.status", "success")
            return result
        except Exception as e:
            span.set_attribute("job.status", "error")
            span.set_attribute("job.error", str(e))
            span.record_exception(e)
            raise

# Trace a request
async def trace_request(request: Request):
    """
    Trace a request and return a ResponseModel
    """
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    return ResponseModel(trace_id=trace_id)

# Extract trace context from request headers
def extract_trace_context(request: Request):
    """
    Extract trace context from request headers
    """
    propagator = TraceContextTextMapPropagator()
    context = propagator.extract(carrier=dict(request.headers))
    return context

tracer = get_tracer()
import time
from typing import Tuple

from fastapi import Request
from opentelemetry import trace
from prometheus_client import (REGISTRY, Counter, Gauge, Histogram,
                               generate_latest)
from starlette.routing import Match
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.config.settings import settings
from app.config.version import __version__

INFO = Gauge(
    "fastapi_app_info", "FastAPI application information.", [
        "app_name", "environment", "version"]
)
REQUESTS = Counter(
    "fastapi_requests_total", "Total count of requests by method and path.", [
        "method", "path", "app_name", "environment", "version"]
)
RESPONSES = Counter(
    "fastapi_responses_total",
    "Total count of responses by method, path and status codes.",
    ["method", "path", "status_code", "app_name", "environment", "version"],
)
REQUESTS_PROCESSING_TIME = Histogram(
    "fastapi_requests_duration_seconds",
    "Histogram of requests processing time by path (in seconds)",
    ["method", "path", "app_name", "environment", "version"],
)
EXCEPTIONS = Counter(
    "fastapi_exceptions_total",
    "Total count of exceptions raised by path and exception type",
    ["method", "path", "exception_type", "app_name", "environment", "version"],
)
REQUESTS_IN_PROGRESS = Gauge(
    "fastapi_requests_in_progress",
    "Gauge of requests by method and path currently being processed",
    ["method", "path", "app_name", "environment", "version"],
)

class MetricsMiddleware:
    def __init__(self):
        self.app_name = settings.app_name
        self.environment = settings.environment
        self.version = __version__
        INFO.labels(app_name=self.app_name, environment=self.environment, version=self.version).inc()

    async def __call__(self, request: Request, call_next):
        method = request.method
        path, is_handled_path = self.get_path(request)

        if not is_handled_path:
            return await call_next(request)
        
        REQUESTS_IN_PROGRESS.labels(
            method=method, path=path, app_name=self.app_name, environment=self.environment, version=self.version).inc()
        REQUESTS.labels(method=method, path=path, app_name=self.app_name, environment=self.environment, version=self.version).inc()
        before_time = time.perf_counter()
        try:
            response = await call_next(request)
        except BaseException as e:
            status_code = response.status_code if 'response' in locals() else HTTP_500_INTERNAL_SERVER_ERROR
            EXCEPTIONS.labels(method=method, path=path, exception_type=type(
                e).__name__, app_name=self.app_name, environment=self.environment, version=self.version).inc()
            raise e from None
        else:
            status_code = response.status_code
            after_time = time.perf_counter()
            exemplar = None
            span = trace.get_current_span()
            span_context = span.get_span_context()
            if span_context and span_context.is_valid:
                trace_id = trace.format_trace_id(span_context.trace_id)
                exemplar = {'TraceID': trace_id}

            REQUESTS_PROCESSING_TIME.labels(method=method, path=path, app_name=self.app_name, environment=self.environment, version=self.version).observe(
                after_time - before_time, exemplar=exemplar
            )
        finally:
            RESPONSES.labels(method=method, path=path,
                             status_code=status_code, app_name=self.app_name, environment=self.environment, version=self.version).inc()
            REQUESTS_IN_PROGRESS.labels(
                method=method, path=path, app_name=self.app_name, environment=self.environment, version=self.version).dec()

        return response
    
    @staticmethod
    def get_path(request: Request) -> Tuple[str, bool]:
        for route in request.app.routes:
            match, child_scope = route.matches(request.scope)
            if match == Match.FULL:
                return route.path, True

        return request.url.path, False
metrics_middleware = MetricsMiddleware()
    
def metrics():
    return generate_latest(REGISTRY)
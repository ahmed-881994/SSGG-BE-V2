import asyncio
import os
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pymysql import DataError, IntegrityError

from app.api import (auth, entities, events, health, lookups, members,
                     permissions, roles, users, visualizer, metrics)
from app.config.logging_config import logger
from app.config.settings import settings
from app.config.version import __version__
from app.core.health_metrics import update_health_metrics
from app.core.metrics_middleware import metrics_middleware
from app.services.healthcheck_service import HealthCheckService
from app.core.access_control_middleware import access_control_middleware
from app.core.auditing_middleware import auditing_middleware
from app.core.exceptions import (AuthenticationFailed, EntityDoesNotExistError,
                                 InvalidOperationError, InvalidTokenError,
                                 ServiceError, SSGGApiError)
from app.core.logging_middleware import logging_middleware
from app.core.rate_limitting import setup_rate_limiting
from app.core.user_context_middleware import user_context_middleware
from app.schemas.common_schema import ErrorResponse


# Add lifespan to the application
@asynccontextmanager
async def lifespan(app: FastAPI):
    async def _health_metrics_loop():
        service = HealthCheckService()
        while True:
            try:
                report = await service.check_health(summary_only=False)
                update_health_metrics(report)
            except Exception as exc:
                logger.warning(f"Health metrics collection failed: {exc}")
            await asyncio.sleep(30)

    task = asyncio.create_task(_health_metrics_loop())
    logger.info("Application started — health metrics collection running")
    try:
        yield
    finally:
        task.cancel()
        logger.info("Application shutdown")

app = FastAPI(
    title="SSGG",
    summary="This is the documentation for the backend APIs for the Sporting Scouts and Girl Guides members management app",
    version=__version__,
    responses={
        200: {"description": "Successful response"},
        201: {"description": "Resource created successfully"},
        400: {"description": "Bad request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
        503: {"description": "Service unavailable", "model": ErrorResponse},
    },
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[s for s in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
app.middleware("http")(metrics_middleware)
app.middleware("http")(access_control_middleware)
app.middleware("http")(user_context_middleware)
app.middleware("http")(auditing_middleware)
@app.middleware("http")
async def add_logging_middleware(request: Request, call_next):
    return await logging_middleware(request, call_next)

# Setup rate limiting
setup_rate_limiting(app)



tags_metadata = [
    {
        "name": "Members",
        "description": "Operations for managing member profiles, including registration, updates, queries, and membership status management. Handles individual member data and their associated roles.",
    },
    {
        "name": "Events",
        "description": "Endpoints for managing SSGG events, including creation, scheduling, registration, attendance tracking, and event reporting. Supports both one-time and recurring events.",
    },
    {
        "name": "Entities",
        "description": "Management of organizational entities such as teams, groups, and workgroups. Includes hierarchy management, entity relationships, and administrative operations.",
    },
    {
        "name": "Authentication",
        "description": "Security endpoints for user authentication, token management, and authorization. Handles login, token refresh, password reset, and session management.",
    },
    {
        "name": "Lookups",
        "description": "Reference data endpoints providing access to system-wide lookup tables, including member types, roles, ranks, badges, and other standardized classifications used across the application.",
    },
    {
        "name": "Roles",
        "description": "Endpoints for managing user roles and permissions within the SSGG system. Includes role creation, updates, deletions, and permission assignments to control access to various features and data.",
    },
    {
        "name": "Permissions",
        "description": "Management of permissions associated with roles and users. Endpoints to create, update, delete, and query permissions that define access levels within the SSGG application.",
    },
    {
        "name": "Health",
        "description": "Health check endpoints to monitor the status and performance of the SSGG backend services. Provides basic uptime and diagnostics information.",
    },
    {
        "name": "Users",
        "description": "User management endpoints for creating, updating, retrieving, and deleting user accounts. Handles user profiles, roles, and access permissions within the SSGG system.",
    },
    {   "name": "Visualizer",
        "description": "Endpoints for executing visualization queries and retrieving data for graphical representations. Supports custom query execution and data formatting for visual analytics.",
    },
]

app.openapi_tags = tags_metadata


# ------------------------------#
# API routes
# ------------------------------#
app.include_router(auth.router)
app.include_router(members.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(entities.router)
app.include_router(lookups.router)
app.include_router(health.router)
app.include_router(roles.router)
app.include_router(permissions.router)
app.include_router(visualizer.router)
app.include_router(metrics.router)


# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve favicon.ico
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join("static", "favicon.ico"))


def create_exception_handler(status_code: int, initial_detail: str) -> Callable[[Request, Exception], JSONResponse]:
    # Using a dictionary to hold the detail
    detail = {"message": initial_detail}

    def exception_handler(_: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, SSGGApiError):
            if exc.message:
                detail["message"] = exc.message

            if exc.name:
                detail["message"] = f"{detail['message']} [{exc.name}]"

            logger.error(exc)
            return JSONResponse(
                status_code=status_code, content={"detail": detail["message"]}
            )
        # Default response for other exceptions
        logger.error(exc)
        return JSONResponse(
            status_code=500, content={"detail": "An unexpected error occurred."}
        )

    return exception_handler


app.add_exception_handler(
    exc_class_or_status_code=EntityDoesNotExistError,
    handler=create_exception_handler(
        status.HTTP_404_NOT_FOUND, "Entity does not exist."),
)

app.add_exception_handler(
    exc_class_or_status_code=InvalidOperationError,
    handler=create_exception_handler(
        status.HTTP_400_BAD_REQUEST, "Can't perform the operation."
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=IntegrityError,
    handler=create_exception_handler(
        status.HTTP_400_BAD_REQUEST, "Can't process the request due to integrity error."
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=DataError,
    handler=create_exception_handler(
        status.HTTP_400_BAD_REQUEST, "Data can't be processed, check the input."
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=AuthenticationFailed,
    handler=create_exception_handler(
        status.HTTP_401_UNAUTHORIZED, "Authentication failed due to invalid credentials.",),
)

app.add_exception_handler(
    exc_class_or_status_code=InvalidTokenError,
    handler=create_exception_handler(
        status.HTTP_401_UNAUTHORIZED, "Invalid token, please re-authenticate again."
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=ServiceError,
    handler=create_exception_handler(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "A service seems to be down, try again later.",
    ),
)
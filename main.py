import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, events, members, teams
from app.schema.common import ErrorResponse

logger = logging.getLogger('uvicorn.error')
#logger.setLevel(logging.ERROR)


app = FastAPI(title="SSGG", summary="This is the documentation for the backend APIs for the Sporting Scouts and Girl Guides members management app", version="2.0.0", responses={
    400: {"description": "Bad request", "model": ErrorResponse},
    500: {"description": "Internal server error", "model": ErrorResponse},
}, on_startup=None)

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # required
    allow_credentials=True,           # allow cookies/credentials
    # or ["*"] :contentReference[oaicite:1]{index=1}
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    # or e.g. ["Authorization","Content-Type"] :contentReference[oaicite:2]{index=2}
    allow_headers=["*"],
)

tags_metadata = [
    {
        "name": "Members",
        "description": "Everything about Members.",
    },
    {
        "name": "Teams",
        "description": "Everything about Teams.",
    },
    {
        "name": "Events",
        "description": "Everything about Events.",
    },
]

app.openapi_tags = tags_metadata


# ------------------------------#
# API routes
# ------------------------------#
app.include_router(auth.router)
app.include_router(members.router)
app.include_router(teams.router)
app.include_router(events.router)


# ------------------------------#
# Health check endpoint
# ------------------------------#
@app.get("/", include_in_schema=False)
def read_root():
    """Health check endpoint.
    This endpoint is used to check if the SSGG-V2 application is running.

    Returns:
        Dict: A dictionary with a welcome message.
        - message (str): A welcome message indicating the application is running.
    """
    return {"message": "Welcome to the SSGG-V2 API!"}


@app.exception_handler(Exception)
async def http_exception_handler(request, exc):
    """
    Custom exception handler for HTTPException.
    This function handles HTTP exceptions and returns a JSON response with the error details.

    Args:
        request: The HTTP request object.
        exc: The HTTPException object.

    Returns:
        JSONResponse: A JSON response containing the error details.
    """
    logger.error(f"HTTPException: {exc.detail}")
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {request.headers}")
    logger.info(f"Body: {await request.body()}")
    logger.info(f"Query Params: {request.query_params}")
    logger.info(f"Path Params: {request.path_params}")
    logger.info(f"Client: {request.client.host}:{request.client.port}")
    logger.info(f"Exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

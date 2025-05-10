import logging
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymysql import DataError, IntegrityError

from app.api import auth, events, members, teams
from app.exceptions.exceptions import AuthenticationFailed, EntityDoesNotExistError, InvalidOperationError, InvalidTokenError, SSGGApiError, ServiceError
from app.schema.common import ErrorResponse

logger = logging.getLogger('uvicorn.error')


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
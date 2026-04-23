from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from app.core.exceptions import (
    AppException,
    ValidationError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    DatabaseError
)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "status": exc.status_code
        }
    )


async def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message,
            "status": 400,
            "error_type": "validation_error"
        }
    )


async def conflict_error_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": exc.message,
            "status": 409,
            "error_type": "conflict_error"
        }
    )


async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": exc.message,
            "status": 404,
            "error_type": "not_found_error"
        }
    )


async def unauthorized_error_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": exc.message,
            "status": 401,
            "error_type": "unauthorized_error"
        },
        headers={"WWW-Authenticate": "Bearer"}
    )


async def database_error_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "status": 500,
            "error_type": "database_error"
        }
    )


EXCEPTION_HANDLERS = {
    AppException: app_exception_handler,
    ValidationError: validation_error_handler,
    ConflictError: conflict_error_handler,
    NotFoundError: not_found_error_handler,
    UnauthorizedError: unauthorized_error_handler,
    DatabaseError: database_error_handler,
}

import logging
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from bson.errors import InvalidId
from app.core.config import settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on FastAPI application."""

    @app.exception_handler(InvalidId)
    async def invalid_id_exception_handler(request: Request, exc: InvalidId) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.warning("InvalidId Exception [req_id:%s]: %s", request_id, str(exc))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_OBJECT_ID",
                    "message": "The provided ID format is invalid.",
                    "details": None,
                },
            },
        )


    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.warning(
            "AppException [%s]: %s (code: %s) [req_id:%s]",
            exc.status_code,
            exc.message,
            exc.error_code,
            request_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.warning(
            "HTTPException [%s]: %s [req_id:%s]",
            exc.status_code,
            exc.detail,
            request_id,
        )
        error_code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = "UNAUTHORIZED"
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            error_code = "FORBIDDEN"
        elif exc.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "NOT_FOUND"

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": error_code,
                    "message": str(exc.detail),
                    "details": None,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.warning("RequestValidationError [req_id:%s]: %s", request_id, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters or payload.",
                    "details": jsonable_encoder(exc.errors()),
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.error(
            "Unhandled Exception [req_id:%s]: %s",
            request_id,
            str(exc),
            exc_info=True,
        )

        message = (
            "An unexpected error occurred."
            if not settings.DEBUG
            else f"Internal error: {str(exc)}"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": message,
                    "details": None,
                },
            },
        )

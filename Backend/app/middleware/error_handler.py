import logging
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError, PyMongoError
from app.core.config import settings
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on FastAPI application."""

    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.warning("DuplicateKeyError [req_id:%s]: %s", request_id, str(exc))
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "error": {
                    "code": "CONFLICT",
                    "message": "A record with this information already exists.",
                    "details": None,
                },
            },
        )

    @app.exception_handler(PyMongoError)
    async def pymongo_exception_handler(request: Request, exc: PyMongoError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.error("PyMongoError [req_id:%s]: %s", request_id, str(exc))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Database is temporarily unavailable. Please try again.",
                    "details": None,
                },
            },
        )

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

        # Construct clear, user-friendly validation message from field errors
        field_messages = []
        for err in exc.errors():
            loc = err.get("loc", [])
            field = str(loc[-1]) if loc else "Field"
            field_name = " ".join(field.split("_")).capitalize()
            raw_msg = err.get("msg", "Invalid value")

            if "not a valid email address" in raw_msg.lower():
                clean_msg = "Please enter a valid email address."
            elif "at least 6 characters" in raw_msg.lower():
                clean_msg = "Password must be at least 6 characters long."
            elif "at least 2 characters" in raw_msg.lower():
                clean_msg = "Full name must be at least 2 characters long."
            elif "field required" in raw_msg.lower():
                clean_msg = f"{field_name} is required."
            elif raw_msg.startswith("Value error, "):
                clean_msg = raw_msg[len("Value error, "):].strip()
                if not clean_msg.endswith("."):
                    clean_msg += "."
            else:
                clean_msg = f"{field_name}: {raw_msg}."

            if clean_msg not in field_messages:
                field_messages.append(clean_msg)

        error_message = " ".join(field_messages) if field_messages else "Invalid request parameters or payload."

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": error_message,
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

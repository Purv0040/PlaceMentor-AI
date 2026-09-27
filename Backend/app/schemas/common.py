from typing import Generic, Optional, TypeVar, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str = Field(..., example="NOT_FOUND")
    message: str = Field(..., example="Resource not found.")
    details: Optional[Any] = None


class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


class HealthStatus(BaseModel):
    status: str
    service: str
    database: Optional[str] = None
    redis: Optional[str] = None

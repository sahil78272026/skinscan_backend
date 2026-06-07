from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str

class Envelope(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None
    meta: Optional[dict[str, Any]] = None

def success_response(data: T, meta: Optional[dict[str, Any]] = None) -> Envelope[T]:
    return Envelope(success=True, data=data, meta=meta)

def error_response(code: str, message: str) -> Envelope[Any]:
    return Envelope(success=False, error=ErrorDetail(code=code, message=message))

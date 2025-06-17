from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")

class ResponseSchemas(BaseModel):
    status: str
    message: str
    data: Optional[Union[Dict[str, Any], List[Any]]] = None
    errors: Optional[str] = None


class StandardResponse(BaseModel, Generic[T]):
    """Standard API response model for both success and error responses."""

    status: str = Field(..., description="Status of the response (success or error)")
    message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data payload")
    error: Optional[T] = Field(None, description="error encountered")


class ErrorResponse(StandardResponse):
    data: None
    error: Optional[str] = None

class SuccessResponse(StandardResponse):
    data: T
    error: None
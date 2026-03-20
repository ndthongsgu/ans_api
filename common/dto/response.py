from pydantic import BaseModel
from typing import Optional, Generic, TypeVar

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper"""
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None
    statusCode: int = 200

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation successful",
                "data": None,
                "error": None,
                "statusCode": 200
            }
        }

class SuccessResponse(BaseModel):
    """Success response"""
    success: bool = True
    message: str
    statusCode: int = 200

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    message: str
    error: Optional[str] = None
    statusCode: int = 400

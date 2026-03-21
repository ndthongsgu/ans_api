from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, Any, Dict

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

# Helper functions for standardized responses
def success_response(
    message: str,
    data: Optional[Any] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Create a standardized success response
    
    Args:
        message: Success message to display to user
        data: Optional response data
        status_code: HTTP status code (default: 200)
    
    Returns:
        Dictionary with standardized response format
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
        "statusCode": status_code
    }

def error_response(
    message: str,
    error: Optional[str] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        message: Error message to display to user
        error: Optional technical error details
        status_code: HTTP status code (default: 400)
    
    Returns:
        Dictionary with standardized response format
    """
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": error or message,
        "statusCode": status_code
    }

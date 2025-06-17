from typing import Any, Dict, List, Optional, Union
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from schema.response import ResponseSchemas


def success_response(
    data: Optional[Union[Dict[str, Any], List[Any]]] = None, message: str = "Request Successful", status_code: int = 200
) -> JSONResponse:
    """
     Returns a success response with the given data and message.

    Args:
        data (Any, optional): Defaults to None.
        message (str):  Defaults to "Success".
        status_code (int, optional):  Defaults to 200.

    Returns:
        JSONResponse: it's a dict format with status, message, and data.
    """
    response = ResponseSchemas(
        status="success",
        message=message,
        data=data,
        errors=None,
    )
    return JSONResponse(content=jsonable_encoder(response.model_dump()), status_code=status_code)


def error_response(
    message: str = "An internal server error occurred",
    status_code: int = 500,
    errors: Any = None,
) -> JSONResponse:
    """
    Returns an error response with the given message and errors.

    Args:
        message(str): The error message. Defaults to 'An internal server error occurred'
        status_code (int, optional): The HTTP status code. Defaults to 500.
        errors (Any, optional): Additional error details. Defaults to None.

    Returns:
        JSONResponse: A JSON response containing the error details.
    """
    response = ResponseSchemas(
        status="error", message=message, data=None, errors=errors
    )
    return JSONResponse(content=jsonable_encoder(response.model_dump()), status_code=status_code)

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom exception handler that returns error details directly
    without FastAPI's default {"detail": ...} wrapper.

    - {"error": "Malformed data"} for 400
    - {"error": "Not found"} for 404
    - {"error": "Expected application/json media type"} for 415
    - {"server error": "API response code XXX"} for 500
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

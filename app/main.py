import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.routers import pet_types, pets, pictures
from app.core.exceptions import http_exception_handler


# Create FastAPI application
app = FastAPI(
    title="Pet Store Inventory Management API",
    description="REST API for managing a pet store inventory with integration to Ninja Animals API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handler
app.add_exception_handler(HTTPException, http_exception_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors.
    - Returns 415 for JSON parsing errors or wrong Content-Type
    - Returns 400 for other validation errors (missing fields, type errors)
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        return JSONResponse(
            status_code=415,
            content={"error": "Expected application/json media type"}
        )

    return JSONResponse(
        status_code=400,
        content={"error": "Malformed data"}
    )


# Include routers
app.include_router(pet_types.router)
app.include_router(pets.router)
app.include_router(pictures.router)


@app.get("/kill")
async def kill_process():
    """Kill the container process for testing restart behavior."""
    os._exit(1)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )

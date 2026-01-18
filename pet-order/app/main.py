import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import purchases, transactions


app = FastAPI(
    title="Pet Order Service",
    description="Service for handling pet purchases",
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for Pydantic validation errors."""
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
app.include_router(purchases.router)
app.include_router(transactions.router)


@app.get("/kill")
async def kill_process():
    """Kill the container process for testing restart behavior."""
    os._exit(1)

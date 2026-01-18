from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.models.purchase import PurchaseRequest, PurchaseResponse
from app.services.purchase_service import process_purchase, NoPetAvailable


router = APIRouter(tags=["purchases"])


@router.post("/purchases", status_code=status.HTTP_201_CREATED, response_model=PurchaseResponse)
async def create_purchase(request: Request, purchase: PurchaseRequest):
    """
    Create a purchase.
    - Find available pet based on criteria
    - Delete pet from pet-store
    - Store transaction in MongoDB
    - Return purchase response
    """
    # Validate Content-Type
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        return JSONResponse(
            status_code=415,
            content={"error": "Expected application/json media type"}
        )

    try:
        response = await process_purchase(purchase)
        return response
    except NoPetAvailable:
        return JSONResponse(
            status_code=400,
            content={"error": "No pet of this type is available"}
        )

from typing import Optional
from fastapi import APIRouter, Header, Query, status
from fastapi.responses import JSONResponse

from app.services.purchase_service import get_transactions


router = APIRouter(tags=["transactions"])

OWNER_PC_SECRET = "LovesPetsL2M3n4"


@router.get("/transactions", status_code=status.HTTP_200_OK)
async def list_transactions(
    ownerpc: Optional[str] = Header(None, alias="OwnerPC"),
    store: Optional[int] = Query(None),
    pet_type: Optional[str] = Query(None, alias="pet-type"),
    purchaser: Optional[str] = Query(None),
    purchase_id: Optional[str] = Query(None, alias="purchase-id")
):
    """
    Get transactions with optional filtering.
    Requires OwnerPC header for authentication.
    """
    # Check authentication header
    if ownerpc != OWNER_PC_SECRET:
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized"}
        )

    transactions = get_transactions(
        store=store,
        pet_type=pet_type,
        purchaser=purchaser,
        purchase_id=purchase_id
    )

    # Convert to list of dicts with proper aliases
    return [t.model_dump(by_alias=True) for t in transactions]

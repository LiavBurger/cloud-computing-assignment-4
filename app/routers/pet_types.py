from fastapi import APIRouter, HTTPException, status, Request
from typing import Optional

from app.models.pet_type import PetTypeCreate, PetTypeResponse
from app.services.pet_type_service import pet_type_service


router = APIRouter(prefix="/pet-types", tags=["pet-types"])

ALLOWED_QUERY_PARAMS = {"id", "type", "family", "genus", "lifespan", "hasAttribute"}


@router.post("", response_model=PetTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_pet_type(pet_type: PetTypeCreate, request: Request):
    """
    Create a new pet type by fetching data from Ninja Animals API.

    Returns:
        201: Pet type created successfully
        400: Type not found in Ninja API or type already exists
        415: Wrong content type
        500: Ninja API error
    """
    # Check content type
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        raise HTTPException(
            status_code=415,
            detail={"error": "Expected application/json media type"}
        )

    try:
        return await pet_type_service.create_pet_type(pet_type.type)
    except ValueError as e:
        # Animal not found or pet type already exists
        raise HTTPException(
            status_code=400,
            detail={"error": "Malformed data"}
        )
    except RuntimeError as e:
        # API error
        error_msg = str(e)
        if "API_ERROR:" in error_msg:
            status_code = error_msg.split(":")[1]
            raise HTTPException(
                status_code=500,
                detail={"server error": f"API response code {status_code}"}
            )
        raise HTTPException(
            status_code=500,
            detail={"server error": error_msg}
        )


@router.get("", response_model=list[PetTypeResponse])
async def get_pet_types(
    request: Request,
    id: Optional[str] = None,
    type: Optional[str] = None,
    family: Optional[str] = None,
    genus: Optional[str] = None,
    lifespan: Optional[int] = None,
    hasAttribute: Optional[str] = None
):
    """
    Get all pet types with optional filtering.

    Query Parameters:
        - id: Filter by ID
        - type: Filter by type
        - family: Filter by family
        - genus: Filter by genus
        - lifespan: Filter by lifespan
        - hasAttribute: Filter by attribute

    Returns:
        200: List of pet types (empty array if no matches or unknown query params)
    """
    for param in request.query_params.keys():
        if param not in ALLOWED_QUERY_PARAMS:
            return []

    return pet_type_service.get_all_pet_types(
        id=id,
        type=type,
        family=family,
        genus=genus,
        lifespan=lifespan,
        has_attribute=hasAttribute
    )


@router.get("/{id}", response_model=PetTypeResponse)
async def get_pet_type(id: str):
    """
    Get a specific pet type by ID.

    Returns:
        200: Pet type found
        404: Pet type not found
    """
    pet_type = pet_type_service.get_pet_type(id)
    if not pet_type:
        raise HTTPException(
            status_code=404,
            detail={"error": "Not found"}
        )
    return pet_type


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet_type(id: str):
    """
    Delete a pet type. Can only delete if pets array is empty.

    Returns:
        204: Pet type deleted successfully
        400: Pets array is not empty
        404: Pet type not found
    """
    try:
        pet_type_service.delete_pet_type(id)
        return None
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "PET_TYPE_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={"error": "Not found"}
            )
        raise HTTPException(
            status_code=400,
            detail={"error": "Malformed data"}
        )

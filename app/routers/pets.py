from fastapi import APIRouter, HTTPException, status, Request
from typing import Optional

from app.models.pet import PetCreate, PetUpdate, PetResponse
from app.services.pet_service import pet_service


router = APIRouter(prefix="/pet-types", tags=["pets"])


@router.post("/{id}/pets", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
async def create_pet(id: str, pet: PetCreate, request: Request):
    """
    Add a new pet to a pet type.

    Args:
        id: Pet type ID
        pet: Pet data (name, optional birthdate, optional picture-url)

    Returns:
        201: Pet created successfully
        400: Malformed data (e.g., duplicate name)
        404: Pet type not found
        415: Wrong content type
    """
    # Check content type
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        raise HTTPException(
            status_code=415,
            detail={"error": "Expected application/json media type"}
        )

    try:
        return await pet_service.create_pet(
            pet_type_id=id,
            name=pet.name,
            birthdate=pet.birthdate,
            picture_url=pet.picture_url
        )
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "PET_TYPE_NOT_FOUND":
            raise HTTPException(
                status_code=404,
                detail={"error": "Not found"}
            )
        # DUPLICATE_PET_NAME or INVALID_BIRTHDATE_FORMAT
        raise HTTPException(
            status_code=400,
            detail={"error": "Malformed data"}
        )


@router.get("/{id}/pets", response_model=list[PetResponse])
async def get_pets(
    id: str,
    birthdateGT: Optional[str] = None,
    birthdateLT: Optional[str] = None
):
    """
    Get all pets for a pet type with optional date filtering.

    Args:
        id: Pet type ID
        birthdateGT: Filter pets born after this date (DD-MM-YYYY)
        birthdateLT: Filter pets born before this date (DD-MM-YYYY)

    Returns:
        200: List of pets
        404: Pet type not found
    """
    try:
        return pet_service.get_pets_for_type(
            pet_type_id=id,
            birthdate_gt=birthdateGT,
            birthdate_lt=birthdateLT
        )
    except ValueError:
        # PET_TYPE_NOT_FOUND
        raise HTTPException(
            status_code=404,
            detail={"error": "Not found"}
        )


@router.get("/{id}/pets/{name}", response_model=PetResponse)
async def get_pet(id: str, name: str):
    """
    Get a specific pet.

    Args:
        id: Pet type ID
        name: Pet name

    Returns:
        200: Pet found
        404: Pet type or pet not found
    """
    try:
        pet = pet_service.get_pet(pet_type_id=id, pet_name=name)
        if not pet:
            raise HTTPException(
                status_code=404,
                detail={"error": "Not found"}
            )
        return pet
    except ValueError:
        # PET_TYPE_NOT_FOUND
        raise HTTPException(
            status_code=404,
            detail={"error": "Not found"}
        )


@router.put("/{id}/pets/{name}", response_model=PetResponse)
async def update_pet(id: str, name: str, pet: PetUpdate, request: Request):
    """
    Update a pet.

    Args:
        id: Pet type ID
        name: Pet name (from URL)
        pet: Updated pet data

    Returns:
        200: Pet updated successfully
        400: Malformed data
        404: Pet type or pet not found
        415: Wrong content type
    """
    # Check content type
    content_type = request.headers.get("content-type", "")
    if "application/json" not in content_type:
        raise HTTPException(
            status_code=415,
            detail={"error": "Expected application/json media type"}
        )

    try:
        return await pet_service.update_pet(
            pet_type_id=id,
            pet_name=name,
            name=pet.name,
            birthdate=pet.birthdate,
            picture_url=pet.picture_url
        )
    except ValueError as e:
        error_msg = str(e)
        if error_msg in ["PET_TYPE_NOT_FOUND", "PET_NOT_FOUND"]:
            raise HTTPException(
                status_code=404,
                detail={"error": "Not found"}
            )
        # NAME_MISMATCH or INVALID_BIRTHDATE_FORMAT
        raise HTTPException(
            status_code=400,
            detail={"error": "Malformed data"}
        )


@router.delete("/{id}/pets/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet(id: str, name: str):
    """
    Delete a pet and its picture.

    Args:
        id: Pet type ID
        name: Pet name

    Returns:
        204: Pet deleted successfully
        404: Pet type or pet not found
    """
    try:
        pet_service.delete_pet(pet_type_id=id, pet_name=name)
        return None
    except ValueError:
        # PET_TYPE_NOT_FOUND or PET_NOT_FOUND
        raise HTTPException(
            status_code=404,
            detail={"error": "Not found"}
        )

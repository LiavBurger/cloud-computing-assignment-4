from typing import Optional
import httpx
from app.config import settings


PET_STORE_URLS = {
    1: settings.pet_store1_url,
    2: settings.pet_store2_url
}


async def get_pet_types(store: int) -> list[dict]:
    """Get all pet types from a store."""
    url = f"{PET_STORE_URLS[store]}/pet-types"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        return []


async def find_pet_type_id(store: int, pet_type_name: str) -> Optional[str]:
    """Find pet type ID by name (case-insensitive)."""
    pet_types = await get_pet_types(store)
    pet_type_lower = pet_type_name.lower()
    for pt in pet_types:
        if pt.get("type", "").lower() == pet_type_lower:
            return pt.get("id")
    return None


async def get_pets_for_type(store: int, pet_type_id: str) -> list[dict]:
    """Get all pets for a pet type."""
    url = f"{PET_STORE_URLS[store]}/pet-types/{pet_type_id}/pets"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        return []


async def get_pet(store: int, pet_type_id: str, pet_name: str) -> Optional[dict]:
    """Get a specific pet by name."""
    url = f"{PET_STORE_URLS[store]}/pet-types/{pet_type_id}/pets/{pet_name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        return None


async def delete_pet(store: int, pet_type_id: str, pet_name: str) -> bool:
    """Delete a pet from a store. Returns True if successful."""
    url = f"{PET_STORE_URLS[store]}/pet-types/{pet_type_id}/pets/{pet_name}"
    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
        return response.status_code in [200, 204]

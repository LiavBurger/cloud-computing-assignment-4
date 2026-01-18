from typing import Optional

from app.storage.mongo_store import store
from app.services.ninja_api import ninja_api_service


class PetTypeService:
    """Service for managing pet types."""

    async def create_pet_type(self, pet_type: str) -> dict:
        """
        Create a new pet type by fetching data from Ninja API.

        Args:
            pet_type: The type of pet to create

        Returns:
            The created pet type data

        Raises:
            ValueError: If type exists or not found in API
            RuntimeError: If API error occurs
        """
        # Check if pet type already exists (case-insensitive)
        if store.pet_type_exists(pet_type):
            raise ValueError("PET_TYPE_ALREADY_EXISTS")

        animal_data = await ninja_api_service.fetch_animal_data(pet_type)

        pet_type_id = store.add_pet_type(animal_data)

        return store.get_pet_type(pet_type_id)

    def get_all_pet_types(
        self,
        id: Optional[str] = None,
        type: Optional[str] = None,
        family: Optional[str] = None,
        genus: Optional[str] = None,
        lifespan: Optional[int] = None,
        has_attribute: Optional[str] = None
    ) -> list[dict]:
        """
        Get all pet types with optional filtering.

        Args:
            id: Filter by ID
            type: Filter by type (case-insensitive)
            family: Filter by family (case-insensitive)
            genus: Filter by genus (case-insensitive)
            lifespan: Filter by lifespan
            has_attribute: Filter by attribute (case-insensitive)

        Returns:
            List of pet types matching the filters
        """
        pet_types = store.get_all_pet_types()

        # Apply filters
        if id is not None:
            pet_types = [pt for pt in pet_types if pt["id"] == id]

        if type is not None:
            type_lower = type.lower()
            pet_types = [pt for pt in pet_types if pt["type"].lower() == type_lower]

        if family is not None:
            family_lower = family.lower()
            pet_types = [pt for pt in pet_types if pt["family"].lower() == family_lower]

        if genus is not None:
            genus_lower = genus.lower()
            pet_types = [pt for pt in pet_types if pt["genus"].lower() == genus_lower]

        if lifespan is not None:
            pet_types = [pt for pt in pet_types if pt["lifespan"] == lifespan]

        if has_attribute is not None:
            attr_lower = has_attribute.lower()
            pet_types = [
                pt for pt in pet_types
                if any(attr.lower() == attr_lower for attr in pt["attributes"])
            ]

        return pet_types

    def get_pet_type(self, pet_type_id: str) -> Optional[dict]:
        """
        Get a specific pet type by ID.

        Args:
            pet_type_id: The ID of the pet type

        Returns:
            The pet type data, or None if not found
        """
        return store.get_pet_type(pet_type_id)

    def delete_pet_type(self, pet_type_id: str) -> None:
        """
        Delete a pet type. Can only delete if pets array is empty.

        Args:
            pet_type_id: The ID of the pet type to delete

        Raises:
            ValueError: If pets array not empty or pet type not found
        """
        pet_type = store.get_pet_type(pet_type_id)
        if not pet_type:
            raise ValueError("PET_TYPE_NOT_FOUND")

        # Check if pets array is empty
        if pet_type["pets"]:
            raise ValueError("PET_TYPE_HAS_PETS")

        store.delete_pet_type(pet_type_id)

    def add_pet_name_to_type(self, pet_type_id: str, pet_name: str) -> None:
        """Add a pet name to the pet-type's pets array."""
        store.add_pet_name_to_type(pet_type_id, pet_name)

    def remove_pet_name_from_type(self, pet_type_id: str, pet_name: str) -> None:
        """Remove a pet name from the pet-type's pets array."""
        store.remove_pet_name_from_type(pet_type_id, pet_name)


pet_type_service = PetTypeService()

from typing import Optional

from app.storage.mongo_store import store
from app.services.picture_service import picture_service
from app.services.pet_type_service import pet_type_service
from app.utils.validators import validate_date_format, compare_dates


class PetService:

    async def create_pet(
        self,
        pet_type_id: str,
        name: str,
        birthdate: Optional[str] = None,
        picture_url: Optional[str] = None
    ) -> dict:
        """
        Create a new pet.

        Args:
            pet_type_id: The pet type ID
            name: Name of the pet
            birthdate: Optional birthdate (DD-MM-YYYY)
            picture_url: Optional URL to fetch picture from

        Returns:
            The created pet data

        Raises:
            ValueError: If pet type not found, name exists, or invalid data
        """
        pet_type = store.get_pet_type(pet_type_id)
        if not pet_type:
            raise ValueError("PET_TYPE_NOT_FOUND")

        if store.pet_exists(pet_type_id, name):
            raise ValueError("DUPLICATE_PET_NAME")

        if birthdate and not validate_date_format(birthdate):
            raise ValueError("INVALID_BIRTHDATE_FORMAT")

        picture_filename = "NA"
        if picture_url:
            try:
                picture_filename = await picture_service.download_and_save_picture(
                    picture_url, name, pet_type["type"]
                )
            except ValueError:
                # Invalid image format (not JPEG/PNG) - 400 error
                raise
            except Exception:
                # Network/download errors - continue without picture
                picture_filename = "NA"

        pet_data = {
            "name": name,
            "birthdate": birthdate if birthdate else "NA",
            "picture": picture_filename,
            "picture_url": picture_url  # Store for update comparison
        }

        store.add_pet(pet_type_id, name, pet_data)

        pet_type_service.add_pet_name_to_type(pet_type_id, name)

        return {
            "name": pet_data["name"],
            "birthdate": pet_data["birthdate"],
            "picture": pet_data["picture"]
        }

    def get_pets_for_type(
        self,
        pet_type_id: str,
        birthdate_gt: Optional[str] = None,
        birthdate_lt: Optional[str] = None
    ) -> list[dict]:
        """
        Get all pets for a pet type with optional date filtering.

        Args:
            pet_type_id: The pet type ID
            birthdate_gt: Filter pets born after this date
            birthdate_lt: Filter pets born before this date

        Returns:
            List of pets matching the filters

        Raises:
            ValueError: If pet type not found
        """
        pet_type = store.get_pet_type(pet_type_id)
        if not pet_type:
            raise ValueError("PET_TYPE_NOT_FOUND")

        pets = store.get_pets_for_type(pet_type_id)

        # Apply date filters
        if birthdate_gt:
            pets = [
                pet for pet in pets
                if pet["birthdate"] != "NA" and compare_dates(pet["birthdate"], birthdate_gt) > 0
            ]

        if birthdate_lt:
            pets = [
                pet for pet in pets
                if pet["birthdate"] != "NA" and compare_dates(pet["birthdate"], birthdate_lt) < 0
            ]

        return [
            {
                "name": pet["name"],
                "birthdate": pet["birthdate"],
                "picture": pet["picture"]
            }
            for pet in pets
        ]

    def get_pet(self, pet_type_id: str, pet_name: str) -> Optional[dict]:
        """
        Get a specific pet.

        Args:
            pet_type_id: The pet type ID
            pet_name: Name of the pet

        Returns:
            The pet data, or None if not found

        Raises:
            ValueError: If pet type not found
        """
        pet_type = store.get_pet_type(pet_type_id)
        if not pet_type:
            raise ValueError("PET_TYPE_NOT_FOUND")

        result = store.get_pet_case_insensitive(pet_type_id, pet_name)
        if not result:
            return None

        pet, _ = result
        return {
            "name": pet["name"],
            "birthdate": pet["birthdate"],
            "picture": pet["picture"]
        }

    async def update_pet(
        self,
        pet_type_id: str,
        pet_name: str,
        name: str,
        birthdate: Optional[str] = None,
        picture_url: Optional[str] = None
    ) -> dict:
        """
        Update a pet.

        Args:
            pet_type_id: The pet type ID
            pet_name: Current name of the pet (from URL)
            name: Name from request body (must match pet_name)
            birthdate: Optional new birthdate
            picture_url: Optional new picture URL

        Returns:
            The updated pet data

        Raises:
            ValueError: If not found or malformed data
        """
        # Validate pet type exists
        pet_type = store.get_pet_type(pet_type_id)
        if not pet_type:
            raise ValueError("PET_TYPE_NOT_FOUND")

        # Name must match URL
        if name.lower() != pet_name.lower():
            raise ValueError("NAME_MISMATCH")

        # Get existing pet (case-insensitive)
        result = store.get_pet_case_insensitive(pet_type_id, pet_name)
        if not result:
            raise ValueError("PET_NOT_FOUND")

        pet, actual_name = result

        # Validate birthdate format if provided
        if birthdate and not validate_date_format(birthdate):
            raise ValueError("INVALID_BIRTHDATE_FORMAT")

        # Update birthdate
        if birthdate:
            pet["birthdate"] = birthdate

        # Update picture if new URL provided
        if picture_url:
            # Only fetch if URL is different from previous
            if pet.get("picture_url") != picture_url:
                try:
                    # Delete old picture if exists
                    if pet["picture"] != "NA":
                        picture_service.delete_picture(pet["picture"])

                    # Download new picture
                    new_filename = await picture_service.download_and_save_picture(
                        picture_url, name, pet_type["type"]
                    )
                    pet["picture"] = new_filename
                    pet["picture_url"] = picture_url
                except ValueError:
                    # Invalid image format (not JPEG/PNG) - propagate as 400 error
                    raise
                except Exception:
                    # Network/download errors - keep existing picture
                    pass

        # Return response (without picture_url field)
        return {
            "name": pet["name"],
            "birthdate": pet["birthdate"],
            "picture": pet["picture"]
        }

    def delete_pet(self, pet_type_id: str, pet_name: str) -> None:
        """
        Delete a pet and its picture.

        Args:
            pet_type_id: The pet type ID
            pet_name: Name of the pet

        Raises:
            ValueError: If pet type or pet not found
        """
        pet_type = store.get_pet_type(pet_type_id)
        if not pet_type:
            raise ValueError("PET_TYPE_NOT_FOUND")

        result = store.get_pet_case_insensitive(pet_type_id, pet_name)
        if not result:
            raise ValueError("PET_NOT_FOUND")

        pet, actual_name = result

        # Delete picture file if exists
        if pet["picture"] != "NA":
            picture_service.delete_picture(pet["picture"])

        store.delete_pet(pet_type_id, actual_name)

        pet_type_service.remove_pet_name_from_type(pet_type_id, actual_name)


# Singleton instance
pet_service = PetService()

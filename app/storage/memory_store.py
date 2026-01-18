from typing import Dict, Set, Tuple


class MemoryStore:
    """In-memory storage for pet types and pets."""

    def __init__(self):
        # Pet types storage: id -> pet_type_data
        self.pet_types: Dict[str, dict] = {}

        # Pets storage: (pet_type_id, pet_name) -> pet_data
        self.pets: Dict[Tuple[str, str], dict] = {}

        # Track used IDs to ensure they're never reused
        self.used_ids: Set[str] = set()

        # ID counter for generating unique IDs
        self._id_counter: int = 0

    def generate_id(self) -> str:
        """Generate a unique ID that will never be reused."""
        while True:
            self._id_counter += 1
            new_id = str(self._id_counter)
            if new_id not in self.used_ids:
                self.used_ids.add(new_id)
                return new_id

    def add_pet_type(self, pet_type_data: dict) -> str:
        """Add a new pet type and return its ID."""
        pet_type_id = self.generate_id()
        pet_type_data["id"] = pet_type_id
        self.pet_types[pet_type_id] = pet_type_data
        return pet_type_id

    def get_pet_type(self, pet_type_id: str) -> dict | None:
        """Get a pet type by ID."""
        return self.pet_types.get(pet_type_id)

    def get_all_pet_types(self) -> list[dict]:
        """Get all pet types."""
        return list(self.pet_types.values())

    def delete_pet_type(self, pet_type_id: str) -> bool:
        """Delete a pet type by ID. Returns True if deleted, False if not found."""
        if pet_type_id in self.pet_types:
            del self.pet_types[pet_type_id]
            return True
        return False

    def pet_type_exists(self, pet_type_value: str) -> bool:
        """Check if a pet type with the given type value already exists (case-insensitive)."""
        pet_type_lower = pet_type_value.lower()
        return any(pt["type"].lower() == pet_type_lower for pt in self.pet_types.values())

    def add_pet(self, pet_type_id: str, pet_name: str, pet_data: dict) -> None:
        """Add a pet to a pet type."""
        key = (pet_type_id, pet_name)
        self.pets[key] = pet_data

    def get_pet(self, pet_type_id: str, pet_name: str) -> dict | None:
        """Get a pet by pet type ID and name."""
        key = (pet_type_id, pet_name)
        return self.pets.get(key)

    def get_pets_for_type(self, pet_type_id: str) -> list[dict]:
        """Get all pets for a specific pet type."""
        return [
            pet_data
            for (pt_id, _), pet_data in self.pets.items()
            if pt_id == pet_type_id
        ]

    def delete_pet(self, pet_type_id: str, pet_name: str) -> bool:
        """Delete a pet. Returns True if deleted, False if not found."""
        key = (pet_type_id, pet_name)
        if key in self.pets:
            del self.pets[key]
            return True
        return False

    def pet_exists(self, pet_type_id: str, pet_name: str) -> bool:
        """Check if a pet exists for a pet type (case-insensitive)."""
        pet_name_lower = pet_name.lower()
        return any(
            pt_id == pet_type_id and name.lower() == pet_name_lower
            for (pt_id, name) in self.pets.keys()
        )


store = MemoryStore()

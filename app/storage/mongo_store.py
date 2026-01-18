import re
from typing import Optional, Tuple
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING
from app.database import get_database
from app.config import settings


class MongoStore:
    """MongoDB storage for pet types and pets."""

    def __init__(self, store_name: str):
        self.store_name = store_name
        self._db = None
        self._pet_types_collection = None
        self._pets_collection = None
        self._indexes_created = False

    @property
    def db(self):
        """Lazy database connection."""
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def pet_types_collection(self):
        """Get pet_types collection for this store."""
        if self._pet_types_collection is None:
            self._pet_types_collection = self.db[f"pet_types_{self.store_name}"]
        return self._pet_types_collection

    @property
    def pets_collection(self):
        """Get pets collection for this store."""
        if self._pets_collection is None:
            self._pets_collection = self.db[f"pets_{self.store_name}"]
            self._ensure_indexes()
        return self._pets_collection

    def _ensure_indexes(self):
        """Create indexes for pets collection."""
        if not self._indexes_created:
            # Compound unique index for (pet_type_id, name) - case sensitive
            # Note: case-insensitive uniqueness is handled at application level
            self._pets_collection.create_index(
                [("pet_type_id", ASCENDING), ("name", ASCENDING)],
                unique=True
            )
            self._indexes_created = True

    def add_pet_type(self, pet_type_data: dict) -> str:
        """Add a new pet type and return its ID."""
        result = self.pet_types_collection.insert_one(pet_type_data)
        return str(result.inserted_id)

    def get_pet_type(self, pet_type_id: str) -> Optional[dict]:
        """Get a pet type by ID."""
        try:
            doc = self.pet_types_collection.find_one({"_id": ObjectId(pet_type_id)})
        except InvalidId:
            return None
        if doc:
            doc["id"] = str(doc.pop("_id"))
            return doc
        return None

    def get_all_pet_types(self) -> list[dict]:
        """Get all pet types."""
        docs = list(self.pet_types_collection.find())
        for doc in docs:
            doc["id"] = str(doc.pop("_id"))
        return docs

    def delete_pet_type(self, pet_type_id: str) -> bool:
        """Delete a pet type by ID. Returns True if deleted, False if not found."""
        try:
            result = self.pet_types_collection.delete_one({"_id": ObjectId(pet_type_id)})
        except InvalidId:
            return False
        return result.deleted_count > 0

    def pet_type_exists(self, pet_type_value: str) -> bool:
        """Check if a pet type with the given type value already exists (case-insensitive)."""
        pattern = re.compile(f"^{re.escape(pet_type_value)}$", re.IGNORECASE)
        return self.pet_types_collection.find_one({"type": pattern}) is not None

    def add_pet(self, pet_type_id: str, pet_name: str, pet_data: dict) -> None:
        """Add a pet to a pet type."""
        doc = {**pet_data, "pet_type_id": pet_type_id}
        self.pets_collection.insert_one(doc)

    def get_pet(self, pet_type_id: str, pet_name: str) -> Optional[dict]:
        """Get a pet by pet type ID and name (exact match)."""
        doc = self.pets_collection.find_one({
            "pet_type_id": pet_type_id,
            "name": pet_name
        })
        if doc:
            doc.pop("_id", None)
            doc.pop("pet_type_id", None)
            return doc
        return None

    def get_pet_case_insensitive(self, pet_type_id: str, pet_name: str) -> Optional[Tuple[dict, str]]:
        """
        Get pet with case-insensitive name match.
        Returns (pet_data, actual_name) or None.
        """
        pattern = re.compile(f"^{re.escape(pet_name)}$", re.IGNORECASE)
        doc = self.pets_collection.find_one({
            "pet_type_id": pet_type_id,
            "name": pattern
        })
        if doc:
            actual_name = doc["name"]
            doc.pop("_id", None)
            doc.pop("pet_type_id", None)
            return doc, actual_name
        return None

    def get_pets_for_type(self, pet_type_id: str) -> list[dict]:
        """Get all pets for a specific pet type."""
        docs = list(self.pets_collection.find({"pet_type_id": pet_type_id}))
        for doc in docs:
            doc.pop("_id", None)
            doc.pop("pet_type_id", None)
        return docs

    def delete_pet(self, pet_type_id: str, pet_name: str) -> bool:
        """Delete a pet. Returns True if deleted, False if not found."""
        result = self.pets_collection.delete_one({
            "pet_type_id": pet_type_id,
            "name": pet_name
        })
        return result.deleted_count > 0

    def pet_exists(self, pet_type_id: str, pet_name: str) -> bool:
        """Check if a pet exists for a pet type (case-insensitive)."""
        pattern = re.compile(f"^{re.escape(pet_name)}$", re.IGNORECASE)
        return self.pets_collection.find_one({
            "pet_type_id": pet_type_id,
            "name": pattern
        }) is not None

    def add_pet_name_to_type(self, pet_type_id: str, pet_name: str) -> None:
        """Add a pet name to the pet-type's pets array."""
        try:
            self.pet_types_collection.update_one(
                {"_id": ObjectId(pet_type_id)},
                {"$addToSet": {"pets": pet_name}}
            )
        except InvalidId:
            pass

    def remove_pet_name_from_type(self, pet_type_id: str, pet_name: str) -> None:
        """Remove a pet name from the pet-type's pets array."""
        try:
            self.pet_types_collection.update_one(
                {"_id": ObjectId(pet_type_id)},
                {"$pull": {"pets": pet_name}}
            )
        except InvalidId:
            pass


store = MongoStore(settings.store_name)

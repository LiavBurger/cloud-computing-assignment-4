from typing import Optional
import random
from dataclasses import dataclass

from app.models.purchase import PurchaseRequest, PurchaseResponse, Transaction
from app.services import pet_store_client
from app.database import get_transactions_collection


@dataclass
class FoundPet:
    """Represents a found pet that can be purchased."""
    store: int
    pet_type_id: str
    pet_type_name: str
    name: str


class NoPetAvailable(Exception):
    """Raised when no pet of the requested type is available."""
    pass


async def find_available_pet(request: PurchaseRequest) -> Optional[FoundPet]:
    """
    Find an available pet based on the request criteria.
    - If store AND pet-name: find exact pet in that store
    - If only store: find random pet of type in that store
    - If neither: find random pet of type from any store
    """
    stores_to_check = [request.store] if request.store else [1, 2]

    for store in stores_to_check:
        pet_type_id = await pet_store_client.find_pet_type_id(store, request.pet_type)
        if not pet_type_id:
            continue

        if request.pet_name:
            # Find specific pet
            pet = await pet_store_client.get_pet(store, pet_type_id, request.pet_name)
            if pet:
                return FoundPet(
                    store=store,
                    pet_type_id=pet_type_id,
                    pet_type_name=request.pet_type,
                    name=pet["name"]
                )
        else:
            # Find random pet
            pets = await pet_store_client.get_pets_for_type(store, pet_type_id)
            if pets:
                pet = random.choice(pets)
                return FoundPet(
                    store=store,
                    pet_type_id=pet_type_id,
                    pet_type_name=request.pet_type,
                    name=pet["name"]
                )

    return None


async def process_purchase(request: PurchaseRequest) -> PurchaseResponse:
    """
    Process a purchase request.
    1. Find available pet
    2. Delete pet from pet-store
    3. Store transaction in MongoDB
    4. Return response
    """
    # 1. Find available pet
    pet = await find_available_pet(request)
    if not pet:
        raise NoPetAvailable()

    # 2. Delete the pet from pet-store
    success = await pet_store_client.delete_pet(pet.store, pet.pet_type_id, pet.name)
    if not success:
        raise NoPetAvailable()

    # 3. Store transaction in MongoDB
    collection = get_transactions_collection()
    transaction_data = {
        "purchaser": request.purchaser,
        "pet_type": pet.pet_type_name,
        "store": pet.store
    }
    result = collection.insert_one(transaction_data)
    purchase_id = str(result.inserted_id)

    # 4. Return response
    return PurchaseResponse(
        purchaser=request.purchaser,
        pet_type=pet.pet_type_name,
        store=pet.store,
        pet_name=pet.name,
        purchase_id=purchase_id
    )


def get_transactions(
    store: Optional[int] = None,
    pet_type: Optional[str] = None,
    purchaser: Optional[str] = None,
    purchase_id: Optional[str] = None
) -> list[Transaction]:
    """Get transactions with optional filters."""
    collection = get_transactions_collection()

    # Build query
    query = {}
    if store is not None:
        query["store"] = store
    if pet_type is not None:
        query["pet_type"] = pet_type
    if purchaser is not None:
        query["purchaser"] = purchaser
    if purchase_id is not None:
        from bson import ObjectId
        from bson.errors import InvalidId
        try:
            query["_id"] = ObjectId(purchase_id)
        except InvalidId:
            return []

    # Query and convert to Transaction objects
    docs = list(collection.find(query))
    transactions = []
    for doc in docs:
        transactions.append(Transaction(
            purchaser=doc["purchaser"],
            pet_type=doc["pet_type"],
            store=doc["store"],
            purchase_id=str(doc["_id"])
        ))

    return transactions

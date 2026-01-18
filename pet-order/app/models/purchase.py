from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict


class PurchaseRequest(BaseModel):
    """Request body for POST /purchases."""
    model_config = ConfigDict(populate_by_name=True)

    purchaser: str
    pet_type: str = Field(alias="pet-type")
    store: Optional[int] = None
    pet_name: Optional[str] = Field(None, alias="pet-name")

    @model_validator(mode='after')
    def validate_pet_name_requires_store(self):
        if self.pet_name and not self.store:
            raise ValueError("pet-name can only be provided if store is provided")
        if self.store is not None and self.store not in [1, 2]:
            raise ValueError("store must be 1 or 2")
        return self


class PurchaseResponse(BaseModel):
    """Response body for successful purchase (201)."""
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    purchaser: str
    pet_type: str = Field(serialization_alias="pet-type")
    store: int
    pet_name: str = Field(serialization_alias="pet-name")
    purchase_id: str = Field(serialization_alias="purchase-id")


class Transaction(BaseModel):
    """Transaction stored in MongoDB and returned by GET /transactions."""
    model_config = ConfigDict(populate_by_name=True, by_alias=True)

    purchaser: str
    pet_type: str = Field(serialization_alias="pet-type")
    store: int
    purchase_id: str = Field(serialization_alias="purchase-id")

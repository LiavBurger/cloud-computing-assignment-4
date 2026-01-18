from pydantic import BaseModel, Field
from typing import Optional


class PetTypeCreate(BaseModel):
    type: str = Field(..., description="Type of pet (e.g., 'Golden Retriever')")


class PetTypeResponse(BaseModel):
    id: str
    type: str
    family: str
    genus: str
    attributes: list[str]
    lifespan: Optional[int] = None
    pets: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "2",
                "type": "Poodle",
                "family": "Canidae",
                "genus": "Canis",
                "attributes": ["Intelligent", "alert", "active"],
                "lifespan": 16,
                "pets": ["Tony", "Lian", "Jamie"]
            }
        }
    }

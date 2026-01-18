from pydantic import BaseModel, Field
from typing import Optional


class PetCreate(BaseModel):
    name: str = Field(..., description="Name of the pet")
    birthdate: Optional[str] = Field(None, description="Birthdate in DD-MM-YYYY format")
    picture_url: Optional[str] = Field(None, alias="picture-url", description="URL to fetch picture from")

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "name": "Jamie",
                "birthdate": "24-10-2023",
                "picture-url": "https://example.com/dog.jpg"
            }
        }
    }


class PetUpdate(BaseModel):
    name: str = Field(..., description="Name of the pet (must match URL)")
    birthdate: Optional[str] = Field(None, description="Birthdate in DD-MM-YYYY format")
    picture_url: Optional[str] = Field(None, alias="picture-url", description="URL to fetch picture from")

    model_config = {
        "populate_by_name": True
    }


class PetResponse(BaseModel):
    name: str
    birthdate: str = Field(default="NA", description="Birthdate or 'NA'")
    picture: str = Field(default="NA", description="Picture filename or 'NA'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Jamie",
                "birthdate": "24-10-2023",
                "picture": "Jamie-poodle.jpg"
            }
        }
    }

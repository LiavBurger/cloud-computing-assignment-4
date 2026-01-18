import httpx
from typing import Optional

from app.config import settings
from app.utils.validators import parse_lifespan, parse_attributes


class NinjaAPIService:

    def __init__(self):
        self.api_url = settings.ninja_api_url
        self.api_key = settings.ninja_api_key

    async def fetch_animal_data(self, animal_type: str) -> dict:
        """
        Fetch animal data from Ninja Animals API.

        Args:
            animal_type: The type of animal to search for

        Returns:
            Dictionary with extracted data: family, genus, attributes, lifespan

        Raises:
            ValueError: If animal not found
            RuntimeError: If API error occurs
        """
        if not self.api_key:
            raise RuntimeError("API_KEY_NOT_CONFIGURED")

        headers = {"X-Api-Key": self.api_key}
        params = {"name": animal_type}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.api_url,
                    headers=headers,
                    params=params,
                    timeout=10.0
                )

                if response.status_code == 404:
                    raise ValueError("ANIMAL_NOT_FOUND")

                if response.status_code != 200:
                    raise RuntimeError(f"API_ERROR:{response.status_code}")

                data = response.json()

                if not data or len(data) == 0:
                    raise ValueError("ANIMAL_NOT_FOUND")

                animal = self._find_exact_match(data, animal_type)
                if not animal:
                    raise ValueError("ANIMAL_NOT_FOUND")

                return self._extract_animal_data(animal, animal_type)

        except httpx.RequestError as e:
            raise RuntimeError(f"API_CONNECTION_ERROR:{str(e)}")
        except (ValueError, RuntimeError):
            raise
        except Exception as e:
            raise RuntimeError(f"UNEXPECTED_ERROR:{str(e)}")

    def _find_exact_match(self, animals: list, target_name: str) -> Optional[dict]:
        """
        Find an exact name match in the list of animals (case-insensitive).

        Args:
            animals: List of animal dictionaries from API
            target_name: The name to match

        Returns:
            The matching animal dict, or None if not found
        """
        target_lower = target_name.lower()
        for animal in animals:
            if animal.get("name", "").lower() == target_lower:
                return animal
        return None

    def _extract_animal_data(self, animal: dict, animal_type: str) -> dict:
        """
        Extract and format data from Ninja API response.

        Args:
            animal: Animal data from API
            animal_type: The original type searched for

        Returns:
            Dictionary with: type, family, genus, attributes, lifespan
        """
        taxonomy = animal.get("taxonomy", {})
        family = taxonomy.get("family", "")
        genus = taxonomy.get("genus", "")

        characteristics = animal.get("characteristics", {})

        temperament = characteristics.get("temperament")
        group_behavior = characteristics.get("group_behavior")
        attributes = parse_attributes(temperament, group_behavior)

        lifespan_str = characteristics.get("lifespan")
        lifespan = parse_lifespan(lifespan_str)

        return {
            "type": animal_type,
            "family": family,
            "genus": genus,
            "attributes": attributes,
            "lifespan": lifespan,
            "pets": []
        }


ninja_api_service = NinjaAPIService()

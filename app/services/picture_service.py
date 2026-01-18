import httpx
from pathlib import Path
from typing import Optional
from PIL import Image
from io import BytesIO

from app.config import settings
from app.utils.validators import generate_picture_filename


ALLOWED_IMAGE_FORMATS = {"jpeg", "jpg", "png"}


class PictureService:
    def __init__(self):
        self.pictures_dir = Path(settings.pictures_dir)
        self._ensure_pictures_dir()

    def _ensure_pictures_dir(self):
        self.pictures_dir.mkdir(parents=True, exist_ok=True)

    async def download_and_save_picture(
        self,
        picture_url: str,
        pet_name: str,
        pet_type: str
    ) -> str:
        """
        Download a picture from URL and save it to the file system.

        Args:
            picture_url: URL to download the image from
            pet_name: Name of the pet (for filename)
            pet_type: Type of the pet (for filename)

        Returns:
            Filename of the saved picture

        Raises:
            Exception if download or save fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(picture_url, timeout=30.0)
                response.raise_for_status()

                image = Image.open(BytesIO(response.content))
                extension = image.format.lower() if image.format else "jpg"

                if extension not in ALLOWED_IMAGE_FORMATS:
                    raise ValueError("INVALID_IMAGE_FORMAT")

                # Generate unique filename
                filename = generate_picture_filename(pet_name, pet_type, extension)
                file_path = self.pictures_dir / filename

                image.save(file_path)

                return filename

        except httpx.RequestError as e:
            raise Exception(f"Failed to download picture: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to save picture: {str(e)}")

    def delete_picture(self, filename: str) -> bool:
        if filename == "NA":
            return False

        file_path = self.pictures_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def get_picture_path(self, filename: str) -> Optional[Path]:
        if filename == "NA":
            return None

        file_path = self.pictures_dir / filename
        if file_path.exists():
            return file_path
        return None

    def picture_exists(self, filename: str) -> bool:
        if filename == "NA":
            return False
        file_path = self.pictures_dir / filename
        return file_path.exists()


picture_service = PictureService()

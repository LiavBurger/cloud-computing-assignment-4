from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import mimetypes

from app.services.picture_service import picture_service


router = APIRouter(prefix="/pictures", tags=["pictures"])

# using /{file_name} instead of /{file-name} because hyphen doesn't work well with FastAPI path parameters
@router.get("/{file_name}")
async def get_picture(file_name: str):
    """
    Retrieve a picture file.

    Args:
        file_name: Name of the picture file

    Returns:
        200: Picture file with appropriate content-type
        404: Picture file not found
    """
    picture_path = picture_service.get_picture_path(file_name)

    if not picture_path:
        raise HTTPException(
            status_code=404,
            detail={"error": "Not found"}
        )

    content_type, _ = mimetypes.guess_type(str(picture_path))
    if not content_type:
        content_type = "application/octet-stream"

    return FileResponse(
        path=picture_path,
        media_type=content_type,
        filename=file_name
    )

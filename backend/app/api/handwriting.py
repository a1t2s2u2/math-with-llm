from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services import gemini_vision

router = APIRouter(prefix="/handwriting", tags=["handwriting"])


class ConvertResponse(BaseModel):
    latex: str


@router.post("/convert", response_model=ConvertResponse)
async def convert_handwriting(file: UploadFile = File(...)) -> ConvertResponse:
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=400, detail="Only PNG or JPEG images are supported"
        )

    content = await file.read()
    mime_type = file.content_type or "image/png"

    try:
        latex = gemini_vision.image_to_latex(content, mime_type)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to convert image: {e}"
        ) from e

    return ConvertResponse(latex=latex)

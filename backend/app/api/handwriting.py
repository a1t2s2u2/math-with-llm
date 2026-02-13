import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import settings
from app.services import gemini_vision

router = APIRouter(prefix="/handwriting", tags=["handwriting"])


class ConvertResponse(BaseModel):
    latex: str
    image_path: str


@router.post("/convert", response_model=ConvertResponse)
async def convert_handwriting(file: UploadFile = File(...)) -> ConvertResponse:
    """手書き数式画像をLaTeXコードに変換する。

    Args:
        file: PNG/JPEG形式の画像ファイル

    Returns:
        変換されたLaTeXコードと保存された画像パス

    Raises:
        HTTPException: ファイル形式が不正、APIキー未設定、認識失敗時
    """
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=400, detail="Only PNG or JPEG images are supported"
        )

    storage_dir = settings.handwriting_storage_path
    storage_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.png"
    image_path = storage_dir / filename

    content = await file.read()
    image_path.write_bytes(content)

    try:
        latex = gemini_vision.image_to_latex(image_path)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to convert image: {e}"
        ) from e

    # PROJECT_ROOT = config.pyから2階層上
    project_root = Path(__file__).parent.parent.parent.parent
    relative_path = image_path.relative_to(project_root)

    return ConvertResponse(latex=latex, image_path=str(relative_path))

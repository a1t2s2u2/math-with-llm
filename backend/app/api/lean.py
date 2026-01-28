from fastapi import APIRouter
from pydantic import BaseModel

from app.models.lean import LeanCheckResult
from app.services import lean

router = APIRouter(prefix="/lean", tags=["lean"])


class LeanCheckRequest(BaseModel):
    lean_code: str
    imports: list[str] = []


@router.post("/check", response_model=LeanCheckResult)
def check_lean_endpoint(request: LeanCheckRequest) -> LeanCheckResult:
    return lean.check_lean(request.lean_code, request.imports)

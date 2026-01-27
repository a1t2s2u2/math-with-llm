from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.llm import LeanGeneration, PatchResult, SkeletonResponse
from app.services import llm, storage

router = APIRouter(prefix="/assist", tags=["assist"])


class SkeletonRequest(BaseModel):
    note_id: str
    block_id: str


class LeanGenerateRequest(BaseModel):
    note_id: str
    block_id: str


class LeanFixRequest(BaseModel):
    lean_code: str
    diagnostics: list[dict]


@router.post("/skeleton", response_model=SkeletonResponse)
def generate_skeleton_endpoint(request: SkeletonRequest) -> SkeletonResponse:
    note = storage.get_note(request.note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    block = next((b for b in note.blocks if b.id == request.block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    vars_context = "\n".join([f"{s.name}" for s in note.symbols])
    context = f"Variables: {vars_context}\n\nNote: {note.title}"

    return llm.generate_skeleton(block, context)


@router.post("/lean/generate", response_model=LeanGeneration)
def generate_lean_endpoint(request: LeanGenerateRequest) -> LeanGeneration:
    note = storage.get_note(request.note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    block = next((b for b in note.blocks if b.id == request.block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    vars_context = "\n".join([f"{s.name}" for s in note.symbols])
    context = f"Note: {note.title}"

    return llm.generate_lean(block, vars_context, context)


@router.post("/lean/fix", response_model=PatchResult)
def generate_fix_endpoint(request: LeanFixRequest) -> PatchResult:
    return llm.generate_fix_patch(request.lean_code, request.diagnostics)

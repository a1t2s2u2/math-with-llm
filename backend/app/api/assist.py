from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.llm import LeanGeneration, PatchResult, SkeletonResponse
from app.services import file_storage, llm, storage

router = APIRouter(prefix="/assist", tags=["assist"])


class SkeletonRequest(BaseModel):
    note_id: str
    block_id: str


class FileSkeletonRequest(BaseModel):
    file_path: str
    block_id: str


class LeanGenerateRequest(BaseModel):
    note_id: str
    block_id: str


class FileLeanGenerateRequest(BaseModel):
    file_path: str
    block_id: str


class LeanFixRequest(BaseModel):
    lean_code: str
    diagnostics: list[dict]


class ChatRequest(BaseModel):
    message: str
    context_type: str | None = None  # 'block' or 'selection'
    context_content: str | None = None


@router.post("/skeleton", response_model=SkeletonResponse)
def generate_skeleton_endpoint(request: SkeletonRequest) -> SkeletonResponse:
    note = storage.get_note(request.note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    block = next((b for b in note.blocks if b.id == request.block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    context = f"Note: {note.title}"

    return llm.generate_skeleton(block, context)


@router.post("/file/skeleton", response_model=SkeletonResponse)
def generate_file_skeleton_endpoint(request: FileSkeletonRequest) -> SkeletonResponse:
    try:
        file_content = file_storage.read_file(request.file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found") from None

    block = next((b for b in file_content.blocks if b.id == request.block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    context = f"File: {file_content.name}"

    return llm.generate_skeleton(block, context)


@router.post("/lean/generate", response_model=LeanGeneration)
def generate_lean_endpoint(request: LeanGenerateRequest) -> LeanGeneration:
    note = storage.get_note(request.note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    block = next((b for b in note.blocks if b.id == request.block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    context = f"Note: {note.title}"

    return llm.generate_lean(block, "", context)


@router.post("/file/lean/generate", response_model=LeanGeneration)
def generate_file_lean_endpoint(request: FileLeanGenerateRequest) -> LeanGeneration:
    try:
        file_content = file_storage.read_file(request.file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found") from None

    block = next((b for b in file_content.blocks if b.id == request.block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    context = f"File: {file_content.name}"

    return llm.generate_lean(block, "", context)


@router.post("/lean/fix", response_model=PatchResult)
def generate_fix_endpoint(request: LeanFixRequest) -> PatchResult:
    return llm.generate_fix_patch(request.lean_code, request.diagnostics)


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    response = llm.chat(request.message, request.context_type, request.context_content)
    return ChatResponse(response=response)

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.llm import LeanGeneration, PatchResult, SkeletonResponse
from app.services import file_storage, llm

router = APIRouter(prefix="/assist", tags=["assist"])


class SkeletonRequest(BaseModel):
    file_path: str
    block_id: str


class LeanGenerateRequest(BaseModel):
    file_path: str
    block_id: str


class LeanFixRequest(BaseModel):
    lean_code: str
    diagnostics: list[dict]


class ChatRequest(BaseModel):
    message: str
    context_type: Literal["block", "selection"] | None = None
    context_content: str | None = None


@router.post("/skeleton", response_model=SkeletonResponse)
def generate_skeleton_endpoint(request: SkeletonRequest) -> SkeletonResponse:
    file_content = file_storage.read_file(request.file_path)

    block = next((b for b in file_content.blocks if b.id == request.block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    context = f"File: {file_content.name}"

    return llm.generate_skeleton(block, context)


@router.post("/lean/generate", response_model=LeanGeneration)
def generate_lean_endpoint(request: LeanGenerateRequest) -> LeanGeneration:
    file_content = file_storage.read_file(request.file_path)

    block = next((b for b in file_content.blocks if b.id == request.block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    context = f"File: {file_content.name}"

    return llm.generate_lean(block, context)


@router.post("/lean/fix", response_model=PatchResult)
def generate_fix_endpoint(request: LeanFixRequest) -> PatchResult:
    return llm.generate_fix_patch(request.lean_code, request.diagnostics)


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    response = llm.chat(request.message, request.context_type, request.context_content)
    return ChatResponse(response=response)

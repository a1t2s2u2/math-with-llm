import json
from collections.abc import Generator
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models.block import Block
from app.models.llm import SkeletonResponse
from app.services import file_storage, llm

router = APIRouter(prefix="/assist", tags=["assist"])


def _find_block(file_path: str, block_id: str) -> tuple[Block, str]:
    """IDでブロックを検索し、コンテキスト文字列とともに返す。未検出時は404。"""
    file_content = file_storage.read_file(file_path)
    block = next((b for b in file_content.blocks if b.id == block_id), None)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return block, f"File: {file_content.name}"


class SkeletonRequest(BaseModel):
    file_path: str
    block_id: str


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    context_type: Literal["block", "selection"] | None = None
    context_content: str | None = None
    file_path: str | None = None
    block_id: str | None = None
    history: list[ChatHistoryItem] = []


@router.post("/skeleton", response_model=SkeletonResponse)
def generate_skeleton_endpoint(request: SkeletonRequest) -> SkeletonResponse:
    block, context = _find_block(request.file_path, request.block_id)
    return llm.generate_skeleton(block, context)


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    response = llm.chat(request.message, request.context_type, request.context_content)
    return ChatResponse(response=response)


@router.post("/chat/stream")
def chat_stream_endpoint(request: ChatRequest) -> StreamingResponse:
    history = [{"role": h.role, "content": h.content} for h in request.history]

    if request.file_path and request.block_id:
        file_content = file_storage.read_file(request.file_path)
        return StreamingResponse(
            _generate_with_tools(
                request.message,
                request.context_content,
                request.block_id,
                file_content.blocks,
                history,
            ),
            media_type="text/event-stream",
        )

    def generate() -> Generator[str, None, None]:
        for chunk in llm.chat_stream(
            request.message, request.context_type, request.context_content, history
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


def _generate_with_tools(
    message: str,
    context_content: str | None,
    block_id: str,
    blocks: list[Block],
    history: list[dict[str, str]],
) -> Generator[str, None, None]:
    for event in llm.chat_stream_with_tools(
        message, context_content, block_id, blocks, history
    ):
        yield f"data: {json.dumps(event)}\n\n"
    yield "data: [DONE]\n\n"

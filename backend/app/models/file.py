from typing import Literal

from pydantic import BaseModel

from app.models.block import Block


class FileNode(BaseModel):
    name: str
    type: Literal["file", "directory"]
    path: str
    children: list["FileNode"] | None = None


class FileContent(BaseModel):
    path: str
    name: str
    content: str
    rendered_html: str
    blocks: list[Block]

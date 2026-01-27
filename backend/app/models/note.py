from enum import Enum

from pydantic import BaseModel, Field


class BlockType(str, Enum):
    DEFINITION = "definition"
    LEMMA = "lemma"
    THEOREM = "theorem"
    PROPOSITION = "proposition"
    COROLLARY = "corollary"
    PROOF = "proof"
    REMARK = "remark"
    EXAMPLE = "example"


class Block(BaseModel):
    type: BlockType
    label: str | None = None
    id: str
    range: tuple[int, int]
    latex_fragment: str


class Symbol(BaseModel):
    name: str
    first_occurrence_pos: int


class Todo(BaseModel):
    content: str
    line_number: int


class LeanArtifact(BaseModel):
    block_id: str
    lean_code: str | None = None
    diagnostics: list[dict] = Field(default_factory=list)
    logs: str | None = None
    patches: list[str] = Field(default_factory=list)


class Note(BaseModel):
    note_id: str
    title: str
    latex_source: str = ""
    blocks: list[Block] = Field(default_factory=list)
    symbols: list[Symbol] = Field(default_factory=list)
    todos: list[Todo] = Field(default_factory=list)
    lean_artifacts: dict[str, LeanArtifact] = Field(default_factory=dict)


class NoteCreate(BaseModel):
    title: str


class NoteUpdate(BaseModel):
    latex_source: str

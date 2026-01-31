from enum import Enum

from pydantic import BaseModel


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
    title: str | None = None
    id: str
    range: tuple[int, int]
    latex_fragment: str


class ParseResult(BaseModel):
    blocks: list[Block]
    renderer_errors: list[str] = []

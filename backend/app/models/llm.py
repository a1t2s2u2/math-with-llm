from pydantic import BaseModel


class SkeletonCard(BaseModel):
    strategy: str
    description: str
    required_lemmas: list[str] = []
    assumptions_to_check: list[str] = []


class SkeletonResponse(BaseModel):
    cards: list[SkeletonCard]


class BlockReference(BaseModel):
    id: str
    type: str
    title: str | None = None

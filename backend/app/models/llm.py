from pydantic import BaseModel


class SkeletonCard(BaseModel):
    strategy: str
    description: str
    required_lemmas: list[str] = []
    assumptions_to_check: list[str] = []


class SkeletonResponse(BaseModel):
    cards: list[SkeletonCard]


class LeanGeneration(BaseModel):
    lean_code: str
    imports: list[str] = []
    notes: str = ""


class PatchResult(BaseModel):
    patch: str
    description: str

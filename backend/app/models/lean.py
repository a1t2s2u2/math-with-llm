from pydantic import BaseModel


class Diagnostic(BaseModel):
    line: int
    column: int
    severity: str
    message: str


class LeanCheckResult(BaseModel):
    status: str
    diagnostics: list[Diagnostic] = []
    logs: str = ""
    duration_ms: int = 0

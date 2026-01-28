from pydantic import BaseModel


class ParseResult(BaseModel):
    blocks: list
    symbols: list
    todos: list
    renderer_errors: list[str] = []

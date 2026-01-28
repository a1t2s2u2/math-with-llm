from pydantic import BaseModel


class ParseResult(BaseModel):
    blocks: list
    todos: list
    renderer_errors: list[str] = []

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.block import ParseResult
from app.services import parser

router = APIRouter(prefix="/parse", tags=["parse"])


class ParseRequest(BaseModel):
    latex_source: str


@router.post("", response_model=ParseResult)
def parse_latex_endpoint(request: ParseRequest) -> ParseResult:
    return parser.parse_latex(request.latex_source)

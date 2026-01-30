from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import assist, files, git, lean, parse
from app.config import settings

app = FastAPI(title="math-with-llm API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(FileNotFoundError)
def handle_file_not_found(_request: Request, exc: FileNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(FileExistsError)
def handle_file_exists(_request: Request, exc: FileExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ValueError)
def handle_value_error(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(parse.router)
app.include_router(assist.router)
app.include_router(lean.router)
app.include_router(files.router)
app.include_router(git.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

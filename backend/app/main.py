from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import assist, files, lean, notes, parse
from app.config import settings

app = FastAPI(title="math-with-llm API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router)
app.include_router(parse.router)
app.include_router(assist.router)
app.include_router(lean.router)
app.include_router(files.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

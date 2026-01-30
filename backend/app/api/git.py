from fastapi import APIRouter
from pydantic import BaseModel

from app.models.git import GitCommitResult, GitDiff, GitStatus
from app.services import git as git_service

router = APIRouter(prefix="/git", tags=["git"])


class StageRequest(BaseModel):
    paths: list[str]


class CommitRequest(BaseModel):
    message: str


@router.get("/status")
def status() -> GitStatus:
    return git_service.get_status()


@router.get("/diff")
def diff(path: str, staged: bool = False) -> GitDiff:
    return git_service.get_diff(path, staged)


@router.get("/original")
def original(path: str) -> dict[str, str]:
    content = git_service.get_original(path)
    return {"content": content}


@router.post("/init")
def init() -> dict[str, str]:
    git_service.init_repo()
    return {"status": "ok"}


@router.post("/stage")
def stage(body: StageRequest) -> dict[str, str]:
    git_service.stage_files(body.paths)
    return {"status": "ok"}


@router.post("/unstage")
def unstage(body: StageRequest) -> dict[str, str]:
    git_service.unstage_files(body.paths)
    return {"status": "ok"}


@router.post("/discard")
def discard(body: StageRequest) -> dict[str, str]:
    git_service.discard_files(body.paths)
    return {"status": "ok"}


@router.post("/commit")
def commit(body: CommitRequest) -> GitCommitResult:
    return git_service.commit(body.message)

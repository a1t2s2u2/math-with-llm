from fastapi import APIRouter
from pydantic import BaseModel

from app.models.git import GitCommitResult, GitDiff, GitStatus
from app.services import git as git_service

router = APIRouter(prefix="/git", tags=["git"])


class StageRequest(BaseModel):
    paths: list[str]


class CommitRequest(BaseModel):
    message: str


class StatusResponse(BaseModel):
    status: str


@router.get("/status")
def status() -> GitStatus:
    """Gitステータスを取得する。"""
    return git_service.get_status()


@router.get("/diff")
def diff(path: str, staged: bool = False) -> GitDiff:
    """指定パスのdiffを取得する。"""
    return git_service.get_diff(path, staged)


@router.get("/original")
def original(path: str) -> dict[str, str]:
    """ファイルのHEADバージョンを取得する。"""
    content = git_service.get_original(path)
    return {"content": content}


@router.post("/init")
def init() -> StatusResponse:
    """Gitリポジトリを初期化する。"""
    git_service.init_repo()
    return StatusResponse(status="ok")


@router.post("/stage")
def stage(body: StageRequest) -> StatusResponse:
    """ファイルをステージングする。"""
    git_service.stage_files(body.paths)
    return StatusResponse(status="ok")


@router.post("/unstage")
def unstage(body: StageRequest) -> StatusResponse:
    """ファイルをアンステージする。"""
    git_service.unstage_files(body.paths)
    return StatusResponse(status="ok")


@router.post("/discard")
def discard(body: StageRequest) -> StatusResponse:
    """ワーキングツリーの変更を破棄する。"""
    git_service.discard_files(body.paths)
    return StatusResponse(status="ok")


@router.post("/commit")
def commit(body: CommitRequest) -> GitCommitResult:
    """コミットを作成する。"""
    return git_service.commit(body.message)

from pydantic import BaseModel


class GitFileStatus(BaseModel):
    path: str
    status: str  # modified, added, deleted, renamed, untracked
    staged: bool


class GitStatus(BaseModel):
    is_repo: bool
    branch: str
    staged: list[GitFileStatus]
    unstaged: list[GitFileStatus]


class GitDiff(BaseModel):
    path: str
    old_content: str
    new_content: str


class GitCommitResult(BaseModel):
    hash: str
    message: str

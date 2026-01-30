import subprocess
from pathlib import Path

from app.models.git import GitCommitResult, GitDiff, GitFileStatus, GitStatus
from app.services.file_storage import get_workspace_path

_STATUS_MAP = {
    "M": "modified",
    "A": "added",
    "D": "deleted",
    "R": "renamed",
    "?": "untracked",
}


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    cwd = get_workspace_path()
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=10,
    )


def is_repo() -> bool:
    workspace = Path(get_workspace_path())
    return (workspace / ".git").exists()


def init_repo() -> None:
    _run_git("init")


def get_status() -> GitStatus:
    if not is_repo():
        return GitStatus(is_repo=False, branch="", staged=[], unstaged=[])

    # Get branch name
    branch_result = _run_git("branch", "--show-current")
    branch = branch_result.stdout.strip()

    # Get porcelain status
    result = _run_git("status", "--porcelain=v1")
    staged: list[GitFileStatus] = []
    unstaged: list[GitFileStatus] = []

    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        index_status = line[0]
        worktree_status = line[1]
        path = line[3:]

        # Handle renames: "R  old -> new"
        if " -> " in path:
            path = path.split(" -> ", 1)[1]

        if index_status == "?":
            unstaged.append(GitFileStatus(path=path, status="untracked", staged=False))
            continue

        if index_status != " ":
            status = _STATUS_MAP.get(index_status, "modified")
            staged.append(GitFileStatus(path=path, status=status, staged=True))

        if worktree_status != " ":
            status = _STATUS_MAP.get(worktree_status, "modified")
            unstaged.append(GitFileStatus(path=path, status=status, staged=False))

    return GitStatus(is_repo=True, branch=branch, staged=staged, unstaged=unstaged)


def get_diff(path: str, staged: bool) -> GitDiff:
    if staged:
        # Compare HEAD vs index
        old_result = _run_git("show", f"HEAD:{path}")
        old_content = old_result.stdout if old_result.returncode == 0 else ""
        new_result = _run_git("show", f":{path}")
        new_content = new_result.stdout if new_result.returncode == 0 else ""
    else:
        # Compare index vs working tree
        index_result = _run_git("show", f":{path}")
        if index_result.returncode == 0:
            old_content = index_result.stdout
        else:
            # Untracked file: no old content
            old_content = ""

        workspace = get_workspace_path()
        file_path = Path(workspace) / path
        new_content = (
            file_path.read_text(encoding="utf-8") if file_path.exists() else ""
        )

    return GitDiff(path=path, old_content=old_content, new_content=new_content)


def get_original(path: str) -> str:
    """Return the HEAD version of a file. Empty string if not committed yet."""
    result = _run_git("show", f"HEAD:{path}")
    return result.stdout if result.returncode == 0 else ""


def stage_files(paths: list[str]) -> None:
    _run_git("add", "--", *paths)


def unstage_files(paths: list[str]) -> None:
    _run_git("reset", "HEAD", "--", *paths)


def discard_files(paths: list[str]) -> None:
    """Discard working tree changes. Untracked files are removed."""
    tracked = []
    untracked = []
    result = _run_git("status", "--porcelain=v1")
    untracked_set = set()
    for line in result.stdout.splitlines():
        if len(line) >= 4 and line[0] == "?":
            untracked_set.add(line[3:])
    for p in paths:
        if p in untracked_set:
            untracked.append(p)
        else:
            tracked.append(p)
    if tracked:
        _run_git("checkout", "HEAD", "--", *tracked)
    if untracked:
        workspace = Path(get_workspace_path())
        for p in untracked:
            fp = workspace / p
            if fp.is_file():
                fp.unlink()


def commit(message: str) -> GitCommitResult:
    _run_git("commit", "-m", message)
    result = _run_git("log", "-1", "--format=%H")
    commit_hash = result.stdout.strip()
    return GitCommitResult(hash=commit_hash, message=message)

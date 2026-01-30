import subprocess
from pathlib import Path

from app.config import settings
from app.models.file import FileContent, FileNode
from app.services.parser import parse_latex
from app.services.renderer import render_latex_to_html

_workspace_root: Path | None = None


def _get_workspace_root() -> Path:
    root = _workspace_root if _workspace_root is not None else settings.workspace_root
    root.mkdir(parents=True, exist_ok=True)
    return root


def set_workspace_root(path: str) -> list[FileNode]:
    """Set workspace root and return file tree."""
    global _workspace_root  # noqa: PLW0603
    resolved = Path(path).resolve()
    if not resolved.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")
    _workspace_root = resolved
    return get_tree()


def get_workspace_path() -> str:
    """Return the absolute path of the current workspace root."""
    return str(_get_workspace_root().resolve())


def pick_directory() -> str:
    """Open native folder selection dialog and return selected path."""
    result = subprocess.run(
        ["osascript", "-e", 'POSIX path of (choose folder with prompt "Open Folder")'],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().rstrip("/")


def browse_directory(path: str | None) -> dict:
    """List subdirectories in the given path for folder browsing."""
    target = Path(path).resolve() if path else Path.home()
    if not target.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")
    dirs: list[str] = []
    for item in sorted(target.iterdir(), key=lambda x: x.name.lower()):
        if item.name.startswith("."):
            continue
        if item.is_dir():
            dirs.append(item.name)
    return {"current": str(target), "dirs": dirs}


def _validate_path(path: str) -> Path:
    """Validate and resolve path within workspace root."""
    root = _get_workspace_root()
    full_path = (root / path).resolve()
    if not str(full_path).startswith(str(root.resolve())):
        raise ValueError("Path traversal not allowed")
    return full_path


def get_tree() -> list[FileNode]:
    """Get directory tree of workspace."""
    root = _get_workspace_root()
    return _build_tree(root, root)


def _build_tree(path: Path, root: Path) -> list[FileNode]:
    nodes: list[FileNode] = []
    try:
        items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        return nodes

    for item in items:
        if item.name.startswith("."):
            continue
        rel_path = str(item.relative_to(root))
        if item.is_dir():
            nodes.append(
                FileNode(
                    name=item.name,
                    type="directory",
                    path=rel_path,
                    children=_build_tree(item, root),
                )
            )
        elif item.suffix == ".tex":
            nodes.append(
                FileNode(
                    name=item.name,
                    type="file",
                    path=rel_path,
                )
            )
    return nodes


def read_file(path: str) -> FileContent:
    """Read file and return parsed content."""
    full_path = _validate_path(path)
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not full_path.is_file():
        raise ValueError(f"Not a file: {path}")

    content = full_path.read_text(encoding="utf-8")
    parse_result = parse_latex(content)
    render_result = render_latex_to_html(content)

    return FileContent(
        path=path,
        name=full_path.name,
        content=content,
        rendered_html=render_result.html,
        blocks=parse_result.blocks,
        todos=parse_result.todos,
    )


def write_file(path: str, content: str) -> FileContent:
    """Write content to file and return parsed result."""
    full_path = _validate_path(path)
    if not full_path.parent.exists():
        raise FileNotFoundError(f"Parent directory not found: {path}")

    full_path.write_text(content, encoding="utf-8")
    return read_file(path)


def create_file(path: str, content: str = "") -> FileContent:
    """Create new file."""
    full_path = _validate_path(path)
    if full_path.exists():
        raise FileExistsError(f"File already exists: {path}")
    if not full_path.parent.exists():
        raise FileNotFoundError(f"Parent directory not found: {path}")

    full_path.write_text(content, encoding="utf-8")
    return read_file(path)


def delete_file(path: str) -> None:
    """Delete file."""
    full_path = _validate_path(path)
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not full_path.is_file():
        raise ValueError(f"Not a file: {path}")

    full_path.unlink()


def rename_file(old_path: str, new_path: str) -> FileContent:
    """Rename or move file."""
    old_full = _validate_path(old_path)
    new_full = _validate_path(new_path)

    if not old_full.exists():
        raise FileNotFoundError(f"File not found: {old_path}")
    if new_full.exists():
        raise FileExistsError(f"Target already exists: {new_path}")
    if not new_full.parent.exists():
        raise FileNotFoundError(f"Target directory not found: {new_path}")

    old_full.rename(new_full)
    return read_file(new_path)


def create_folder(path: str) -> FileNode:
    """Create new folder."""
    full_path = _validate_path(path)
    if full_path.exists():
        raise FileExistsError(f"Path already exists: {path}")

    full_path.mkdir(parents=False, exist_ok=False)
    return FileNode(
        name=full_path.name,
        type="directory",
        path=path,
        children=[],
    )


def delete_folder(path: str) -> None:
    """Delete empty folder."""
    full_path = _validate_path(path)
    if not full_path.exists():
        raise FileNotFoundError(f"Folder not found: {path}")
    if not full_path.is_dir():
        raise ValueError(f"Not a directory: {path}")
    if any(full_path.iterdir()):
        raise ValueError(f"Directory not empty: {path}")

    full_path.rmdir()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.file import FileContent, FileNode
from app.services import file_storage

router = APIRouter(prefix="/files", tags=["files"])


class WriteFileRequest(BaseModel):
    content: str


class CreateFileRequest(BaseModel):
    path: str
    content: str = ""


class RenameRequest(BaseModel):
    old_path: str
    new_path: str


class CreateFolderRequest(BaseModel):
    path: str


class WorkspaceRequest(BaseModel):
    path: str


@router.get("/workspace")
def get_workspace() -> dict[str, str]:
    """Get current workspace root path."""
    return {"path": file_storage.get_workspace_path()}


@router.get("/workspace/browse")
def browse_workspace(path: str | None = None) -> dict:
    """Browse directories for workspace selection."""
    try:
        return file_storage.browse_directory(path)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/workspace", response_model=list[FileNode])
def change_workspace(req: WorkspaceRequest) -> list[FileNode]:
    """Change workspace root directory."""
    try:
        return file_storage.set_workspace_root(req.path)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/tree", response_model=list[FileNode])
def get_tree() -> list[FileNode]:
    """Get directory tree of workspace."""
    return file_storage.get_tree()


@router.get("/{path:path}", response_model=FileContent)
def get_file(path: str) -> FileContent:
    """Get file content with parsed data."""
    return file_storage.read_file(path)


@router.put("/{path:path}", response_model=FileContent)
def update_file(path: str, req: WriteFileRequest) -> FileContent:
    """Update file content."""
    return file_storage.write_file(path, req.content)


@router.post("", response_model=FileContent)
def create_file(req: CreateFileRequest) -> FileContent:
    """Create new file."""
    return file_storage.create_file(req.path, req.content)


@router.delete("/{path:path}")
def delete_file(path: str) -> dict[str, str]:
    """Delete file."""
    file_storage.delete_file(path)
    return {"status": "deleted"}


@router.post("/rename", response_model=FileContent)
def rename_file(req: RenameRequest) -> FileContent:
    """Rename or move file."""
    return file_storage.rename_file(req.old_path, req.new_path)


@router.post("/folders", response_model=FileNode)
def create_folder(req: CreateFolderRequest) -> FileNode:
    """Create new folder."""
    return file_storage.create_folder(req.path)


@router.delete("/folders/{path:path}")
def delete_folder(path: str) -> dict[str, str]:
    """Delete empty folder."""
    file_storage.delete_folder(path)
    return {"status": "deleted"}

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import file_storage
from app.services.file_storage import FileContent, FileNode

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


@router.get("/tree", response_model=list[FileNode])
def get_tree() -> list[FileNode]:
    """Get directory tree of workspace."""
    return file_storage.get_tree()


@router.get("/{path:path}", response_model=FileContent)
def get_file(path: str) -> FileContent:
    """Get file content with parsed data."""
    try:
        return file_storage.read_file(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.put("/{path:path}", response_model=FileContent)
def update_file(path: str, req: WriteFileRequest) -> FileContent:
    """Update file content."""
    try:
        return file_storage.write_file(path, req.content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("", response_model=FileContent)
def create_file(req: CreateFileRequest) -> FileContent:
    """Create new file."""
    try:
        return file_storage.create_file(req.path, req.content)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from None
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/{path:path}")
def delete_file(path: str) -> dict[str, str]:
    """Delete file."""
    try:
        file_storage.delete_file(path)
        return {"status": "deleted"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/rename", response_model=FileContent)
def rename_file(req: RenameRequest) -> FileContent:
    """Rename or move file."""
    try:
        return file_storage.rename_file(req.old_path, req.new_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/folders", response_model=FileNode)
def create_folder(req: CreateFolderRequest) -> FileNode:
    """Create new folder."""
    try:
        return file_storage.create_folder(req.path)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.delete("/folders/{path:path}")
def delete_folder(path: str) -> dict[str, str]:
    """Delete empty folder."""
    try:
        file_storage.delete_folder(path)
        return {"status": "deleted"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

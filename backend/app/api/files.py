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
    """現在のワークスペースルートパスを取得する。"""
    return {"path": file_storage.get_workspace_path()}


@router.get("/workspace/browse")
def browse_workspace(path: str | None = None) -> dict:
    """ワークスペース選択のためにディレクトリを参照する。"""
    try:
        return file_storage.browse_directory(path)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Permission denied") from e


@router.put("/workspace", response_model=list[FileNode])
def change_workspace(req: WorkspaceRequest) -> list[FileNode]:
    """ワークスペースルートディレクトリを変更する。"""
    try:
        return file_storage.set_workspace_root(req.path)
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/workspace/pick")
def pick_workspace() -> dict:
    """ネイティブフォルダピッカーを開きワークスペースを設定する。"""
    path = file_storage.pick_directory()
    if not path:
        return {"tree": None}
    tree = file_storage.set_workspace_root(path)
    return {"tree": tree, "path": path}


@router.get("/tree", response_model=list[FileNode])
def get_tree() -> list[FileNode]:
    """ワークスペースのディレクトリツリーを取得する。"""
    return file_storage.get_tree()


@router.get("/{path:path}", response_model=FileContent)
def get_file(path: str) -> FileContent:
    """ファイル内容をパースデータ付きで取得する。"""
    return file_storage.read_file(path)


@router.put("/{path:path}", response_model=FileContent)
def update_file(path: str, req: WriteFileRequest) -> FileContent:
    """ファイル内容を更新する。"""
    return file_storage.write_file(path, req.content)


@router.post("", response_model=FileContent)
def create_file(req: CreateFileRequest) -> FileContent:
    """新規ファイルを作成する。"""
    return file_storage.create_file(req.path, req.content)


@router.delete("/{path:path}")
def delete_file(path: str) -> dict[str, str]:
    """ファイルを削除する。"""
    file_storage.delete_file(path)
    return {"status": "deleted"}


@router.post("/rename", response_model=FileContent)
def rename_file(req: RenameRequest) -> FileContent:
    """ファイルをリネームまたは移動する。"""
    return file_storage.rename_file(req.old_path, req.new_path)


@router.post("/folders", response_model=FileNode)
def create_folder(req: CreateFolderRequest) -> FileNode:
    """新規フォルダを作成する。"""
    return file_storage.create_folder(req.path)


@router.delete("/folders/{path:path}")
def delete_folder(path: str) -> dict[str, str]:
    """空フォルダを削除する。"""
    file_storage.delete_folder(path)
    return {"status": "deleted"}

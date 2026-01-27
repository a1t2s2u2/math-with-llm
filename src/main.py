import json
from datetime import datetime
from pathlib import Path


def greet(name: str) -> str:
    """挨拶メッセージを生成する.

    Args:
        name: 挨拶する相手の名前

    Returns:
        挨拶メッセージ
    """
    return f"こんにちは、{name}さん！"


def get_info() -> dict[str, str]:
    """システム情報を取得する.

    Returns:
        現在時刻とプロジェクトルートパスを含む辞書
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_root = Path(__file__).parent.parent
    return {
        "current_time": current_time,
        "project_root": str(project_root),
    }


def main() -> None:
    """メインアプリケーションを実行する."""
    message = greet("世界")
    print(message)

    info = get_info()
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

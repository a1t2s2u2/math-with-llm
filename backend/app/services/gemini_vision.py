from pathlib import Path

from google import genai

from app.config import settings


def get_gemini_client() -> genai.Client:
    """Gemini APIクライアントを返す。"""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    return genai.Client(api_key=settings.gemini_api_key)


def image_to_latex(image_path: Path) -> str:
    """手書き数式画像をLaTeXコードに変換する。

    Args:
        image_path: 変換対象の画像ファイルパス

    Returns:
        LaTeXコード文字列

    Raises:
        ValueError: Gemini APIキーが未設定の場合
        FileNotFoundError: 画像ファイルが存在しない場合
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    client = get_gemini_client()

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = """あなたは数式認識の専門家です。
画像に書かれた手書き数式をLaTeX形式に変換してください。

要件:
- LaTeXコードのみを出力（説明不要）
- インライン数式なら $...$ で囲む
- ディスプレイ数式なら $$...$$ で囲む
- 複数の数式がある場合は改行で区切る
- 認識できない場合は「認識できませんでした」と返す
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            genai.types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            prompt,
        ],
    )

    return response.text.strip()

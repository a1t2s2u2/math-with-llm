import warnings
from pathlib import Path

import google.generativeai as genai

from app.config import settings


def configure_gemini() -> genai.GenerativeModel:
    # google.generativeaiの非推奨警告を抑制（google.genaiへの移行は将来対応）
    warnings.filterwarnings(
        "ignore", category=FutureWarning, module="google.generativeai"
    )
    """Gemini APIを設定してモデルを返す。"""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel("gemini-2.0-flash-exp")


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

    model = configure_gemini()

    with open(image_path, "rb") as f:
        image_data = f.read()

    prompt = """あなたは数式認識の専門家です。
画像に書かれた手書き数式をLaTeX形式に変換してください。

要件:
- LaTeXコードのみを出力（説明不要）
- インライン数式なら $...$ で囲む
- ディスプレイ数式なら $$...$$ で囲む
- 複数の数式がある場合は改行で区切る
- 認識できない場合は「認識できませんでした」と返す
"""

    response = model.generate_content(
        [prompt, {"mime_type": "image/png", "data": image_data}]
    )

    return response.text.strip()

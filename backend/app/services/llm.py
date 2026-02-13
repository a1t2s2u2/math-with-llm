import json
from collections.abc import Generator
from typing import Literal

from openai import OpenAI

from app.config import settings
from app.models.block import Block
from app.models.llm import SkeletonCard, SkeletonResponse

client = OpenAI(api_key=settings.openai_api_key)


def _call_llm(
    system: str,
    prompt: str,
    *,
    json_mode: bool = False,
) -> str:
    """共通LLM呼び出しヘルパー"""
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        **({"response_format": {"type": "json_object"}} if json_mode else {}),
    )
    return response.choices[0].message.content or ""


def generate_skeleton(block: Block, context: str = "") -> SkeletonResponse:
    prompt = f"""あなたは数学の証明アシスタントです。
以下の数学的命題を分析し、証明戦略の候補を提示してください。

命題:
{block.latex_fragment}

コンテキスト:
{context}

2〜3個の証明戦略候補を提示してください。各戦略について:
1. 戦略名（例：「直接証明」「背理法」「数学的帰納法」）
2. アプローチの簡潔な説明
3. 必要になりそうな補題や定理
4. 確認すべき仮定や条件

以下のJSON形式で出力してください:
{{
  "cards": [
    {{
      "strategy": "戦略名",
      "description": "簡潔な説明",
      "required_lemmas": ["補題1", "補題2"],
      "assumptions_to_check": ["確認事項1", "確認事項2"]
    }}
  ]
}}

重要: 完全な証明は提供しないでください。
戦略と確認すべき点のみを提案してください。"""

    result = json.loads(
        _call_llm(
            "あなたは数学の証明アシスタントです。解答ではなく戦略を提案してください。",
            prompt,
            json_mode=True,
        )
    )
    return SkeletonResponse(
        cards=[SkeletonCard(**card) for card in result.get("cards", [])]
    )


def chat(
    message: str,
    context_type: Literal["block", "selection"] | None,
    context_content: str | None,
) -> str:
    context_text = ""
    if context_type and context_content:
        if context_type == "block":
            context_text = f"\n\n参照しているブロック:\n{context_content}"
        elif context_type == "selection":
            context_text = f"\n\n選択されたテキスト:\n{context_content}"

    return _call_llm(
        "あなたは数学の専門家です。"
        "数式は必ずLaTeX形式で記述してください。"
        "インライン数式は $...$ で囲み、"
        "ディスプレイ数式は $$...$$ で囲んでください。"
        "簡潔かつ正確に回答してください。",
        f"{message}{context_text}",
    )


def _stream_llm(system: str, prompt: str) -> Generator[str, None, None]:
    """ストリーミングLLM呼び出しヘルパー"""
    stream = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def chat_stream(
    message: str,
    context_type: Literal["block", "selection"] | None,
    context_content: str | None,
) -> Generator[str, None, None]:
    context_text = ""
    if context_type and context_content:
        if context_type == "block":
            context_text = f"\n\n参照しているブロック:\n{context_content}"
        elif context_type == "selection":
            context_text = f"\n\n選択されたテキスト:\n{context_content}"

    yield from _stream_llm(
        "あなたは数学の専門家です。"
        "数式は必ずLaTeX形式で記述してください。"
        "インライン数式は $...$ で囲み、"
        "ディスプレイ数式は $$...$$ で囲んでください。"
        "簡潔かつ正確に回答してください。",
        f"{message}{context_text}",
    )

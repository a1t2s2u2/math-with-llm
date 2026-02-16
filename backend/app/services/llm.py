import json
from collections.abc import Generator
from typing import Any, Literal

from openai import OpenAI

from app.config import settings
from app.models.block import Block
from app.models.llm import BlockReference, SkeletonCard, SkeletonResponse

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


def _stream_llm(
    system: str,
    prompt: str,
    history: list[dict[str, str]] | None = None,
) -> Generator[str, None, None]:
    """ストリーミングLLM呼び出しヘルパー"""
    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    stream = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
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
    history: list[dict[str, str]] | None = None,
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
        history,
    )


_MATH_SYSTEM = (
    "あなたは数学の専門家です。"
    "数式は必ずLaTeX形式で記述してください。"
    "インライン数式は $...$ で囲み、"
    "ディスプレイ数式は $$...$$ で囲んでください。"
    "簡潔かつ正確に回答してください。"
)

_GET_BLOCKS_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "get_blocks",
        "description": "指定したIDのブロック（定義・定理・補題等）の内容を取得します。"
        "前後の文脈が必要な場合に使ってください。",
        "parameters": {
            "type": "object",
            "properties": {
                "block_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "取得したいブロックのIDリスト",
                }
            },
            "required": ["block_ids"],
        },
    },
}


def chat_stream_with_tools(
    message: str,
    context_content: str | None,
    block_id: str,
    blocks: list[Block],
    history: list[dict[str, str]] | None = None,
) -> Generator[dict[str, Any], None, None]:
    block_map = {b.id: b for b in blocks}

    current_block = block_map.get(block_id)
    if not current_block:
        yield from _fallback_stream(message, context_content, history)
        return

    outline_lines = []
    for b in blocks:
        marker = " ← 選択中" if b.id == block_id else ""
        title_part = f" ({b.title})" if b.title else ""
        outline_lines.append(f"- [{b.id}] {b.type.value}{title_part}{marker}")
    outline = "\n".join(outline_lines)

    system = (
        f"{_MATH_SYSTEM}\n\n"
        f"## ファイル内のブロック一覧\n{outline}\n\n"
        "回答に他のブロックの内容が必要な場合は get_blocks ツールで取得できます。"
    )

    context_text = f"\n\n選択ブロックの内容:\n{current_block.latex_fragment}"
    if context_content and context_content != current_block.latex_fragment:
        context_text = f"\n\n参照しているブロック:\n{context_content}"

    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": f"{message}{context_text}"})

    references: list[BlockReference] = []

    for _ in range(3):
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            tools=[_GET_BLOCKS_TOOL],
        )
        choice = response.choices[0]

        if choice.finish_reason != "tool_calls":
            break

        messages.append(choice.message.model_dump(exclude_none=True))

        for tool_call in choice.message.tool_calls or []:
            args = json.loads(tool_call.function.arguments)
            block_ids = args.get("block_ids", [])
            results = []
            for bid in block_ids:
                b = block_map.get(bid)
                if b:
                    results.append(f"[{b.id}] {b.type.value}: {b.latex_fragment}")
                    references.append(
                        BlockReference(id=b.id, type=b.type.value, title=b.title)
                    )
                else:
                    results.append(f"[{bid}] not found")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": "\n\n".join(results),
                }
            )

    if references:
        yield {"references": [r.model_dump() for r in references]}

    stream = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield {"content": delta}


def _fallback_stream(
    message: str,
    context_content: str | None,
    history: list[dict[str, str]] | None = None,
) -> Generator[dict[str, Any], None, None]:
    context_text = ""
    if context_content:
        context_text = f"\n\n参照しているブロック:\n{context_content}"
    messages: list[dict[str, Any]] = [{"role": "system", "content": _MATH_SYSTEM}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": f"{message}{context_text}"})
    stream = client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield {"content": delta}

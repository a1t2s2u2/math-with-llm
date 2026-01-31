import json
from typing import Literal

from openai import OpenAI

from app.config import settings
from app.models.block import Block
from app.models.llm import LeanGeneration, PatchResult, SkeletonCard, SkeletonResponse

client = OpenAI(api_key=settings.openai_api_key)


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

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "あなたは数学の証明アシスタントです。"
                "解答ではなく戦略を提案してください。",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return SkeletonResponse(
        cards=[SkeletonCard(**card) for card in result.get("cards", [])]
    )


def generate_lean(block: Block, context: str = "") -> LeanGeneration:
    prompt = f"""Convert the following LaTeX mathematical statement to Lean 4 code.

Statement:
{block.latex_fragment}

Context:
{context}

Generate Lean 4 code with:
1. Necessary imports (list them separately)
2. Type declarations for variables
3. The theorem/lemma/definition structure
4. Use 'sorry' for proof placeholders

Output as JSON:
{{
  "lean_code": "theorem name : statement := by sorry",
  "imports": ["Mathlib.Algebra.Group.Defs", "..."],
  "notes": "Any important notes about the conversion"
}}"""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "You are a Lean 4 code generator. "
                "Generate skeleton code with 'sorry' placeholders.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return LeanGeneration(**result)


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

    prompt = f"""{message}{context_text}"""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたは数学の専門家です。"
                    "数式は必ずLaTeX形式で記述してください。"
                    "インライン数式は $...$ で囲み、"
                    "ディスプレイ数式は $$...$$ で囲んでください。"
                    "簡潔かつ正確に回答してください。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content or ""


def generate_fix_patch(lean_code: str, diagnostics: list[dict]) -> PatchResult:
    diagnostics_str = "\n".join(
        [
            f"Line {d.get('line', '?')}, Col {d.get('column', '?')}: "
            f"{d.get('message', '')}"
            for d in diagnostics
        ]
    )

    prompt = f"""Fix the following Lean 4 code based on error diagnostics.

Lean Code:
{lean_code}

Errors:
{diagnostics_str}

Generate a minimal fix as a unified diff patch. Focus on:
1. Adding missing imports
2. Fixing type annotations
3. Correcting syntax
4. Resolving name resolution issues

Output as JSON:
{{
  "patch": "diff format patch",
  "description": "Brief description of changes"
}}"""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "You are a Lean 4 code fixer. "
                "Generate minimal diff patches.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return PatchResult(**result)

import json

from openai import OpenAI

from app.config import settings
from app.models.llm import LeanGeneration, PatchResult, SkeletonCard, SkeletonResponse
from app.models.note import Block

client = OpenAI(api_key=settings.openai_api_key)


def generate_skeleton(block: Block, context: str = "") -> SkeletonResponse:
    prompt = f"""You are a mathematical proof assistant.
Analyze the following mathematical statement and provide proof strategy candidates.

Statement:
{block.latex_fragment}

Context:
{context}

Provide 2-3 proof strategy candidates. For each strategy:
1. Name the strategy (e.g., "Direct proof", "Proof by contradiction", "Induction")
2. Describe the approach briefly
3. List required lemmas or theorems that might be needed
4. List assumptions or conditions to verify

Output as JSON with this structure:
{{
  "cards": [
    {{
      "strategy": "Strategy name",
      "description": "Brief description",
      "required_lemmas": ["lemma1", "lemma2"],
      "assumptions_to_check": ["assumption1", "assumption2"]
    }}
  ]
}}

IMPORTANT: Do NOT provide definitive proofs.
Only suggest strategies and what to check."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a mathematical proof assistant that "
                "suggests strategies, not solutions.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return SkeletonResponse(
        cards=[SkeletonCard(**card) for card in result.get("cards", [])]
    )


def generate_lean(
    block: Block, vars_context: str = "", context: str = ""
) -> LeanGeneration:
    prompt = f"""Convert the following LaTeX mathematical statement to Lean 4 code.

Statement:
{block.latex_fragment}

Variables:
{vars_context}

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
        model="gpt-4o-mini",
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
        model="gpt-4o-mini",
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

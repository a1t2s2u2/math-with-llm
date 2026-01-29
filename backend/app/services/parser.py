import re

from app.models.block import Block, BlockType, ParseResult, Todo
from app.utils.id_generator import generate_block_id_from_content

BLOCK_TYPES = [
    "definition",
    "lemma",
    "theorem",
    "proposition",
    "corollary",
    "proof",
    "remark",
    "example",
]


def parse_latex(source: str) -> ParseResult:
    blocks = _extract_blocks(source)
    todos = _extract_todos(source)

    return ParseResult(
        blocks=blocks,
        todos=todos,
    )


# proof が参照できるブロックタイプ（定理系）
PROVABLE_BLOCK_TYPES = {"definition", "lemma", "theorem", "proposition", "corollary"}


def _extract_blocks(source: str) -> list[Block]:
    blocks = []

    block_types_pattern = "|".join(BLOCK_TYPES)
    pattern = rf"\\begin{{({block_types_pattern})}}(\[[^\]]*\])?(.*?)\\end{{\1}}"

    for match in re.finditer(pattern, source, re.DOTALL):
        block_type = match.group(1)
        optional_arg = match.group(2)
        content = match.group(3)
        start, end = match.span()

        label = _extract_label(content)
        if label:
            block_id = label
        else:
            block_id = generate_block_id_from_content(block_type, start, content)
        title = _extract_title(optional_arg, content)

        # proof の場合、オプション引数がなければ直前の定理系ブロックのタイトルを参照
        if block_type == "proof" and not optional_arg:
            title = _get_proof_title(blocks)

        blocks.append(
            Block(
                type=BlockType(block_type),
                label=label,
                title=title,
                id=block_id,
                range=(start, end),
                latex_fragment=match.group(0),
            )
        )

    return blocks


def _get_proof_title(preceding_blocks: list[Block]) -> str | None:
    """直前の定理系ブロックのタイトルを取得して「〇〇 の証明」形式で返す"""
    for block in reversed(preceding_blocks):
        if block.type.value in PROVABLE_BLOCK_TYPES:
            if block.title:
                return f"{block.title} の証明"
            return None
    return None


def _extract_title(optional_arg: str | None, content: str) -> str | None:
    # First try optional argument: \begin{definition}[Title here]
    if optional_arg:
        return optional_arg[1:-1].strip()  # Remove [ and ]

    # Otherwise extract first meaningful line from content
    content = content.strip()
    # Remove \label{...} from content
    content = re.sub(r"\\label\{[^}]*\}", "", content).strip()
    if not content:
        return None

    # Get first line and clean it up
    first_line = content.split("\n")[0].strip()
    # Limit length
    if len(first_line) > 60:
        first_line = first_line[:57] + "..."
    return first_line if first_line else None


def _extract_label(content: str) -> str | None:
    match = re.search(r"\\label\{([^}]+)\}", content)
    return match.group(1) if match else None


def _extract_todos(source: str) -> list[Todo]:
    todos = []

    lines = source.split("\n")
    for i, line in enumerate(lines, start=1):
        if "\\todo{" in line:
            match = re.search(r"\\todo\{([^}]+)\}", line)
            if match:
                todos.append(Todo(content=match.group(1), line_number=i))
        elif "TODO:" in line:
            content = line.split("TODO:", 1)[1].strip()
            todos.append(Todo(content=content, line_number=i))

    return todos

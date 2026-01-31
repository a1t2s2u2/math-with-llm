import re

from app.models.block import Block, BlockType, ParseResult
from app.utils.id_generator import generate_block_id_from_content

BLOCK_TYPES = [bt.value for bt in BlockType]

_MAX_TITLE_LENGTH = 60


def parse_latex(source: str) -> ParseResult:
    blocks = _extract_blocks(source)
    return ParseResult(blocks=blocks)


# proof が参照できるブロックタイプ（定理系）
PROVABLE_BLOCK_TYPES = {
    bt.value
    for bt in BlockType
    if bt not in (BlockType.PROOF, BlockType.REMARK, BlockType.EXAMPLE)
}


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
    # オプション引数から取得: \begin{definition}[Title here]
    if optional_arg:
        return optional_arg[1:-1].strip()  # [ と ] を除去

    # オプション引数がなければ本文の先頭行から抽出
    content = content.strip()
    # \label{...} を除去
    content = re.sub(r"\\label\{[^}]*\}", "", content).strip()
    if not content:
        return None

    # 先頭行を取得
    first_line = content.split("\n")[0].strip()
    # 長さ制限
    if len(first_line) > _MAX_TITLE_LENGTH:
        first_line = first_line[:57] + "..."
    return first_line if first_line else None


def _extract_label(content: str) -> str | None:
    match = re.search(r"\\label\{([^}]+)\}", content)
    return match.group(1) if match else None

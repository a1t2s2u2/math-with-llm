import re

from app.models.block import ParseResult
from app.models.note import Block, BlockType, Symbol, Todo
from app.utils.id_generator import generate_block_id

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
    symbols = _extract_symbols(source)
    todos = _extract_todos(source)

    return ParseResult(
        blocks=blocks,
        symbols=symbols,
        todos=todos,
    )


def _extract_blocks(source: str) -> list[Block]:
    blocks = []

    block_types_pattern = "|".join(BLOCK_TYPES)
    pattern = rf"\\begin{{({block_types_pattern})}}(.*?)\\end{{\1}}"

    for match in re.finditer(pattern, source, re.DOTALL):
        block_type = match.group(1)
        content = match.group(2)
        start, end = match.span()

        label = _extract_label(content)
        block_id = label if label else generate_block_id()

        blocks.append(
            Block(
                type=BlockType(block_type),
                label=label,
                id=block_id,
                range=(start, end),
                latex_fragment=match.group(0),
            )
        )

    return blocks


def _extract_label(content: str) -> str | None:
    match = re.search(r"\\label\{([^}]+)\}", content)
    return match.group(1) if match else None


def _extract_symbols(source: str) -> list[Symbol]:
    symbols = []

    vars_pattern = r"\\vars\{([^}]+)\}"
    for match in re.finditer(vars_pattern, source):
        vars_content = match.group(1)
        pos = match.start()

        var_declarations = vars_content.split(",")
        for var_decl in var_declarations:
            var_decl = var_decl.strip()
            if ":" in var_decl:
                vars_part = var_decl.split(":")[0].strip()
                var_names = vars_part.split()
                for var_name in var_names:
                    symbols.append(Symbol(name=var_name, first_occurrence_pos=pos))
            else:
                var_name = var_decl
                symbols.append(Symbol(name=var_name, first_occurrence_pos=pos))

    return symbols


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

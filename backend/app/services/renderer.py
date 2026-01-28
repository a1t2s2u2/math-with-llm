import re
from dataclasses import dataclass

from latex2mathml import converter


@dataclass
class RenderResult:
    html: str
    errors: list[str]


def _get_line_number(source: str, pos: int) -> int:
    """Get 1-based line number from character position."""
    return source[:pos].count("\n") + 1


def render_latex_to_html(source: str) -> RenderResult:
    """Convert LaTeX source to HTML.

    Uses latex2mathml for math expressions and custom regex for structure.
    Adds data-line attributes for scroll synchronization.
    """
    errors: list[str] = []
    html = source
    original_source = source

    try:
        # Step 1: Extract and expand custom commands BEFORE math conversion
        custom_commands = _extract_custom_commands(html)
        for cmd_name, cmd_def in custom_commands.items():
            escaped_def = cmd_def.replace("\\", r"\\")
            html = re.sub(rf"\\{re.escape(cmd_name)}\b", escaped_def, html)

        # Step 2: Convert display math \[...\] with line numbers
        html = _convert_display_math(html, errors, original_source)

        # Step 3: Convert inline math $...$
        html = _convert_inline_math(html, errors)

        # Step 4: Convert LaTeX structure to HTML with line numbers
        html = _convert_structure(html, original_source)

        return RenderResult(html=html, errors=errors)

    except Exception as e:
        errors.append(f"Rendering failed: {str(e)}")
        return RenderResult(html=f"<p>{source}</p>", errors=errors)


def _convert_display_math(html: str, errors: list[str], original_source: str) -> str:
    r"""Convert display math \[...\] to MathML with line numbers."""
    used_positions: set[int] = set()

    def replace_match(match: re.Match[str]) -> str:
        latex_math = match.group(1)
        # Find position in original source
        search_text = f"\\[{latex_math}\\]"
        line_num = 0
        for m in re.finditer(re.escape(search_text), original_source, re.DOTALL):
            if m.start() not in used_positions:
                line_num = _get_line_number(original_source, m.start())
                used_positions.add(m.start())
                break
        try:
            mathml = converter.convert(latex_math)
            return f'<div class="display-math" data-line="{line_num}">{mathml}</div>'
        except Exception as e:
            errors.append(f"Display math error: {str(e)}")
            return match.group(0)

    return re.sub(r"\\\[(.*?)\\\]", replace_match, html, flags=re.DOTALL)


def _convert_inline_math(html: str, errors: list[str]) -> str:
    """Convert inline math $...$ to MathML."""

    def replace_match(match: re.Match[str]) -> str:
        latex_math = match.group(1)
        try:
            mathml = converter.convert(latex_math)
            return f'<span class="inline-math">{mathml}</span>'
        except Exception as e:
            errors.append(f"Inline math error: {str(e)}")
            return match.group(0)

    return re.sub(r"\$([^\$]+)\$", replace_match, html)


def _extract_custom_commands(text: str) -> dict[str, str]:
    """Extract custom commands from preamble."""
    commands: dict[str, str] = {}
    regex = re.compile(r"\\newcommand\{\\([^}]+)\}\{")

    for match in regex.finditer(text):
        cmd_name = match.group(1)
        start_pos = match.end()

        # Count braces to find the end
        brace_count = 1
        end_pos = start_pos
        while brace_count > 0 and end_pos < len(text):
            if text[end_pos] == "{":
                brace_count += 1
            elif text[end_pos] == "}":
                brace_count -= 1
            end_pos += 1

        if brace_count == 0:
            commands[cmd_name] = text[start_pos : end_pos - 1]

    return commands


def _convert_structure(html: str, original_source: str) -> str:
    """Convert LaTeX structure (sections, environments, lists) to HTML.

    Adds data-line attributes for scroll synchronization.
    """
    # Extract and remove preamble
    html = re.sub(r"^[\s\S]*?\\begin\{document\}", "", html)
    html = re.sub(r"\\end\{document\}[\s\S]*$", "", html)

    # Title/author/date
    title_match = re.search(r"\\title\{([^}]*)\}", html)
    author_match = re.search(r"\\author\{([^}]*)\}", html)
    date_match = re.search(r"\\date\{([^}]*)\}", html)

    if title_match and r"\maketitle" in html:
        # Find line number of \maketitle in original
        maketitle_match = re.search(r"\\maketitle", original_source)
        line_num = (
            _get_line_number(original_source, maketitle_match.start())
            if maketitle_match
            else 0
        )
        title_block = f'<div class="latex-title-block" data-line="{line_num}">'
        if title_match:
            title_block += f'<h1 class="latex-title">{title_match.group(1)}</h1>'
        if author_match:
            title_block += f'<div class="latex-author">{author_match.group(1)}</div>'
        if date_match:
            title_block += f'<div class="latex-date">{date_match.group(1)}</div>'
        title_block += "</div>"
        html = html.replace(r"\maketitle", title_block)

    # Remove metadata commands
    html = re.sub(r"\\title\{[^}]*\}", "", html)
    html = re.sub(r"\\author\{[^}]*\}", "", html)
    html = re.sub(r"\\date\{[^}]*\}", "", html)

    # Sections with line numbers
    used_positions: dict[str, set[int]] = {
        "section": set(),
        "subsection": set(),
        "subsubsection": set(),
    }

    def section_replace(
        match: re.Match[str], tag: str, css_class: str, section_type: str
    ) -> str:
        content = match.group(1)
        pattern = rf"\\{section_type}\{{{re.escape(content)}\}}"
        line_num = 0
        for m in re.finditer(pattern, original_source):
            if m.start() not in used_positions[section_type]:
                line_num = _get_line_number(original_source, m.start())
                used_positions[section_type].add(m.start())
                break
        return f'<{tag} class="{css_class}" data-line="{line_num}">{content}</{tag}>'

    html = re.sub(
        r"\\section\{([^}]+)\}",
        lambda m: section_replace(m, "h1", "latex-section", "section"),
        html,
    )
    html = re.sub(
        r"\\subsection\{([^}]+)\}",
        lambda m: section_replace(m, "h2", "latex-subsection", "subsection"),
        html,
    )
    html = re.sub(
        r"\\subsubsection\{([^}]+)\}",
        lambda m: section_replace(m, "h3", "latex-subsubsection", "subsubsection"),
        html,
    )

    # Theorem environments with line numbers
    env_types = [
        "theorem",
        "definition",
        "lemma",
        "proposition",
        "corollary",
        "proof",
        "remark",
        "example",
    ]
    env_used_positions: dict[str, set[int]] = {env: set() for env in env_types}

    for env_type in env_types:
        pattern = (
            rf"\\begin\{{{env_type}\}}(?:\[([^\]]+)\])?([\s\S]*?)\\end\{{{env_type}\}}"
        )

        def env_replace(match: re.Match[str], env: str = env_type) -> str:
            opt_title = match.group(1)
            content = match.group(2).strip()
            # Find line number in original source
            if opt_title:
                search_pattern = rf"\\begin\{{{env}\}}\[{re.escape(opt_title)}\]"
            else:
                search_pattern = rf"\\begin\{{{env}\}}"
            line_num = 0
            for m in re.finditer(search_pattern, original_source):
                if m.start() not in env_used_positions[env]:
                    line_num = _get_line_number(original_source, m.start())
                    env_used_positions[env].add(m.start())
                    break
            heading = f'<div class="env-heading">{env.capitalize()}'
            if opt_title:
                heading += f" ({opt_title})"
            heading += "</div>"
            env_content = f'<div class="env-content">{content}</div>'
            return (
                f'<div class="latex-env {env}" data-line="{line_num}">'
                f"{heading}{env_content}</div>"
            )

        html = re.sub(pattern, env_replace, html)

    # Lists
    html = re.sub(
        r"\\begin\{enumerate\}([\s\S]*?)\\end\{enumerate\}",
        lambda m: '<ol class="latex-list">'
        + "".join(
            f"<li>{item.strip()}</li>"
            for item in re.split(r"\\item\s+", m.group(1))
            if item.strip()
        )
        + "</ol>",
        html,
    )

    html = re.sub(
        r"\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}",
        lambda m: '<ul class="latex-list">'
        + "".join(
            f"<li>{item.strip()}</li>"
            for item in re.split(r"\\item\s+", m.group(1))
            if item.strip()
        )
        + "</ul>",
        html,
    )

    # Paragraphs
    html = re.sub(r"\n\n+", "</p><p>", html)
    html = f"<p>{html}</p>"

    return html

import re
from dataclasses import dataclass

from latex2mathml import converter


@dataclass
class RenderResult:
    html: str
    errors: list[str]


def render_latex_to_html(source: str) -> RenderResult:
    """Convert LaTeX source to HTML.

    Uses latex2mathml for math expressions and custom regex for structure.
    """
    errors = []
    html = source

    try:
        # Step 1: Extract and expand custom commands BEFORE math conversion
        custom_commands = _extract_custom_commands(html)
        for cmd_name, cmd_def in custom_commands.items():
            escaped_def = cmd_def.replace("\\", r"\\")
            html = re.sub(rf"\\{re.escape(cmd_name)}\b", escaped_def, html)

        # Step 2: Convert display math \[...\]
        html = _convert_display_math(html, errors)

        # Step 3: Convert inline math $...$
        html = _convert_inline_math(html, errors)

        # Step 4: Convert LaTeX structure to HTML
        html = _convert_structure(html)

        return RenderResult(html=html, errors=errors)

    except Exception as e:
        errors.append(f"Rendering failed: {str(e)}")
        return RenderResult(html=f"<p>{source}</p>", errors=errors)


def _convert_display_math(html: str, errors: list[str]) -> str:
    r"""Convert display math \[...\] to MathML."""

    def replace_match(match: re.Match[str]) -> str:
        latex_math = match.group(1)
        try:
            mathml = converter.convert(latex_math)
            return f'<div class="display-math">{mathml}</div>'
        except Exception as e:
            errors.append(f"Display math error: {str(e)}")
            return match.group(0)  # Return original on error

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


def _convert_structure(html: str) -> str:
    """Convert LaTeX structure (sections, environments, lists) to HTML.

    Reuses patterns from parser.py but outputs HTML instead of metadata.
    """
    # Extract and remove preamble
    html = re.sub(r"^[\s\S]*?\\begin\{document\}", "", html)
    html = re.sub(r"\\end\{document\}[\s\S]*$", "", html)

    # Title/author/date
    title_match = re.search(r"\\title\{([^}]*)\}", html)
    author_match = re.search(r"\\author\{([^}]*)\}", html)
    date_match = re.search(r"\\date\{([^}]*)\}", html)

    if title_match and r"\maketitle" in html:
        title_block = '<div class="latex-title-block">'
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

    # Sections
    html = re.sub(r"\\section\{([^}]+)\}", r'<h1 class="latex-section">\1</h1>', html)
    html = re.sub(
        r"\\subsection\{([^}]+)\}", r'<h2 class="latex-subsection">\1</h2>', html
    )
    html = re.sub(
        r"\\subsubsection\{([^}]+)\}",
        r'<h3 class="latex-subsubsection">\1</h3>',
        html,
    )

    # Theorem environments
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
    for env_type in env_types:
        pattern = (
            rf"\\begin\{{{env_type}\}}(?:\[([^\]]+)\])?([\s\S]*?)\\end\{{{env_type}\}}"
        )

        def env_replace(match: re.Match[str], env: str = env_type) -> str:
            opt_title = match.group(1)
            content = match.group(2).strip()
            heading = f'<div class="env-heading">{env.capitalize()}'
            if opt_title:
                heading += f" ({opt_title})"
            heading += "</div>"
            env_content = f'<div class="env-content">{content}</div>'
            return f'<div class="latex-env {env}">{heading}{env_content}</div>'

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

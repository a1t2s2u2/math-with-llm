import re
from dataclasses import dataclass

from latex2mathml import converter


@dataclass
class RenderResult:
    html: str
    errors: list[str]


class _PositionTracker:
    def __init__(self, source: str) -> None:
        self._source = source
        self._used: dict[str, set[int]] = {}

    def find_line(self, pattern: str, category: str = "_default") -> int:
        if category not in self._used:
            self._used[category] = set()
        for m in re.finditer(pattern, self._source, re.DOTALL):
            if m.start() not in self._used[category]:
                self._used[category].add(m.start())
                return self._source[: m.start()].count("\n") + 1
        return 0


def render_latex_to_html(source: str) -> RenderResult:
    """LaTeXソースをHTMLに変換する。

    数式にはlatex2mathml、構造にはカスタム正規表現を使用。
    スクロール同期用にdata-line属性を付与する。
    """
    errors: list[str] = []
    html = source
    tracker = _PositionTracker(source)

    # Step 1: 数式変換前にカスタムコマンドを展開
    custom_commands = _extract_custom_commands(html)
    for cmd_name, cmd_def in custom_commands.items():
        escaped_def = cmd_def.replace("\\", r"\\")
        html = re.sub(rf"\\{re.escape(cmd_name)}\b", escaped_def, html)

    # Step 2: ディスプレイ数式 \[...\] を行番号付きで変換
    html = _convert_display_math(html, errors, tracker)

    # Step 3: インライン数式 $...$ を変換
    html = _convert_inline_math(html, errors)

    # Step 4: LaTeX構造をHTMLに変換（行番号付き）
    html = _convert_structure(html, tracker)

    return RenderResult(html=html, errors=errors)


def _convert_display_math(
    html: str, errors: list[str], tracker: _PositionTracker
) -> str:
    r"""ディスプレイ数式 $$...$$ と \[...\] を行番号付きMathMLに変換する。"""

    def replace_double_dollar(match: re.Match[str]) -> str:
        latex_math = match.group(1)
        search_text = re.escape(f"$${latex_math}$$")
        line_num = tracker.find_line(search_text, "display_math_dollar")
        try:
            mathml = converter.convert(latex_math)
            return f'<div class="display-math" data-line="{line_num}">{mathml}</div>'
        except Exception as e:
            errors.append(f"Display math error: {str(e)}")
            return match.group(0)

    def replace_bracket(match: re.Match[str]) -> str:
        latex_math = match.group(1)
        search_text = re.escape(f"\\[{latex_math}\\]")
        line_num = tracker.find_line(search_text, "display_math_bracket")
        try:
            mathml = converter.convert(latex_math)
            return f'<div class="display-math" data-line="{line_num}">{mathml}</div>'
        except Exception as e:
            errors.append(f"Display math error: {str(e)}")
            return match.group(0)

    # $$...$$ を先に処理（より具体的なパターン）
    html = re.sub(r"\$\$(.*?)\$\$", replace_double_dollar, html, flags=re.DOTALL)
    # \[...\] を処理
    html = re.sub(r"\\\[(.*?)\\\]", replace_bracket, html, flags=re.DOTALL)

    return html


def _convert_inline_math(html: str, errors: list[str]) -> str:
    """インライン数式 $...$ をMathMLに変換する。"""

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
    """プリアンブルからカスタムコマンドを抽出する。"""
    commands: dict[str, str] = {}
    regex = re.compile(r"\\newcommand\{\\([^}]+)\}\{")

    for match in regex.finditer(text):
        cmd_name = match.group(1)
        start_pos = match.end()

        # 波括弧を数えて終端を探す
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


def _convert_structure(html: str, tracker: _PositionTracker) -> str:
    """LaTeX構造（セクション・環境・リスト）をHTMLに変換する。

    スクロール同期用にdata-line属性を付与する。
    """
    # プリアンブルを除去
    html = re.sub(r"^[\s\S]*?\\begin\{document\}", "", html)
    html = re.sub(r"\\end\{document\}[\s\S]*$", "", html)

    # タイトル・著者・日付
    title_match = re.search(r"\\title\{([^}]*)\}", html)
    author_match = re.search(r"\\author\{([^}]*)\}", html)
    date_match = re.search(r"\\date\{([^}]*)\}", html)

    if title_match and r"\maketitle" in html:
        line_num = tracker.find_line(r"\\maketitle", "maketitle")
        title_block = f'<div class="latex-title-block" data-line="{line_num}">'
        if title_match:
            title_block += f'<h1 class="latex-title">{title_match.group(1)}</h1>'
        if author_match:
            title_block += f'<div class="latex-author">{author_match.group(1)}</div>'
        if date_match:
            title_block += f'<div class="latex-date">{date_match.group(1)}</div>'
        title_block += "</div>"
        html = html.replace(r"\maketitle", title_block)

    # メタデータコマンドを除去
    html = re.sub(r"\\title\{[^}]*\}", "", html)
    html = re.sub(r"\\author\{[^}]*\}", "", html)
    html = re.sub(r"\\date\{[^}]*\}", "", html)

    # セクション（行番号付き）
    def section_replace(
        match: re.Match[str], tag: str, css_class: str, section_type: str
    ) -> str:
        content = match.group(1)
        pattern = rf"\\{section_type}\{{{re.escape(content)}\}}"
        line_num = tracker.find_line(pattern, section_type)
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

    # 定理環境（行番号付き）
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
            if opt_title:
                search_pattern = rf"\\begin\{{{env}\}}\[{re.escape(opt_title)}\]"
            else:
                search_pattern = rf"\\begin\{{{env}\}}"
            line_num = tracker.find_line(search_pattern, env)
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

    # リスト
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

    # 段落
    html = re.sub(r"\n\n+", "</p><p>", html)
    html = f"<p>{html}</p>"

    return html

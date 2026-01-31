import re
import subprocess
import tempfile
import time
from pathlib import Path

from app.config import settings
from app.models.lean import Diagnostic, LeanCheckResult

TEMPLATE_PATH = Path(__file__).parent.parent.parent.parent / "lean" / "template.lean"


def check_lean(code: str, imports: list[str]) -> LeanCheckResult:
    start_time = time.time()

    template = TEMPLATE_PATH.read_text()

    imports_str = "\n".join(imports)
    full_code = template.replace("{IMPORTS}", imports_str).replace("{CODE}", code)

    temp_file = Path(tempfile.NamedTemporaryFile(suffix=".lean", delete=False).name)
    temp_file.write_text(full_code)

    try:
        result = subprocess.run(
            ["lean", str(temp_file)],
            capture_output=True,
            text=True,
            timeout=settings.lean_timeout,
        )

        duration_ms = int((time.time() - start_time) * 1000)

        diagnostics = _parse_diagnostics(result.stderr)

        if result.returncode == 0:
            status = "success"
        else:
            status = "failure"

        return LeanCheckResult(
            status=status,
            diagnostics=diagnostics,
            logs=result.stdout + "\n" + result.stderr,
            duration_ms=duration_ms,
        )

    except subprocess.TimeoutExpired:
        duration_ms = int((time.time() - start_time) * 1000)
        return LeanCheckResult(
            status="timeout",
            diagnostics=[],
            logs=f"Execution timed out after {settings.lean_timeout} seconds",
            duration_ms=duration_ms,
        )
    finally:
        if temp_file.exists():
            temp_file.unlink()


def _parse_diagnostics(stderr: str) -> list[Diagnostic]:
    diagnostics = []

    pattern = r"([^:]+):(\d+):(\d+):\s*(error|warning):\s*(.+)"
    for match in re.finditer(pattern, stderr):
        diagnostics.append(
            Diagnostic(
                line=int(match.group(2)),
                column=int(match.group(3)),
                severity=match.group(4),
                message=match.group(5).strip(),
            )
        )

    return diagnostics

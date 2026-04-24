"""Format SanitizeResult for CLI output."""
from __future__ import annotations

from patchwork_env.env_sanitizer import SanitizeResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_sanitize_result(result: SanitizeResult) -> str:
    lines: list[str] = []
    label = result.filename or "<stdin>"
    lines.append(_c("1", f"Sanitize report — {label}"))
    lines.append("")

    if not result.has_issues:
        lines.append(_c("32", "  ✔  All entries are clean."))
    else:
        lines.append(_c("31", f"  ✘  {result.total_issues} issue(s) found:"))
        for issue in result.issues:
            lines.append(f"    {_c('33', issue.key)}: {issue.reason}")

    lines.append("")
    lines.append(
        f"  Clean: {_c('32', str(result.total_clean))}  "
        f"Removed: {_c('31', str(result.total_issues))}"
    )
    return "\n".join(lines)


def format_sanitize_summary(results: list[SanitizeResult]) -> str:
    total_clean = sum(r.total_clean for r in results)
    total_issues = sum(r.total_issues for r in results)
    files = len(results)
    lines = [
        _c("1", "Sanitize summary"),
        f"  Files processed : {files}",
        f"  Clean entries   : {_c('32', str(total_clean))}",
        f"  Issues removed  : {_c('31', str(total_issues))}",
    ]
    return "\n".join(lines)

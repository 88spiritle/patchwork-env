"""Format highlighted env-entry results for terminal output."""
from __future__ import annotations

from patchwork_env.env_highlighter import HighlightResult


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_highlight_result(result: HighlightResult) -> str:
    lines: list[str] = []
    lines.append(_c(1, f"Highlighted entries — {result.filename}"))
    lines.append(
        f"  {result.total_highlighted} of {result.total_entries} keys highlighted"
    )
    lines.append("")

    if not result.highlighted:
        lines.append(_c(32, "  ✔ No keys matched the highlight criteria."))
        return "\n".join(lines)

    for rec in result.highlighted:
        reason_tag = f"  [{rec.reason}]" if rec.reason else ""
        key_part = _c(33, rec.entry.key)
        val_part = rec.entry.value if rec.entry.value is not None else ""
        lines.append(f"  ★ {key_part} = {val_part}{reason_tag}")

    return "\n".join(lines)


def format_highlight_summary(result: HighlightResult) -> str:
    ratio = (
        f"{result.total_highlighted}/{result.total_entries}"
        if result.total_entries
        else "0/0"
    )
    status = _c(33, "HIGHLIGHTED") if result.total_highlighted else _c(32, "CLEAN")
    return f"{result.filename}: {status} ({ratio} keys matched)"

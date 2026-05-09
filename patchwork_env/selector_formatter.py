"""Formatter for SelectionResult."""
from __future__ import annotations

from patchwork_env.env_selector import SelectionResult


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_selection_result(result: SelectionResult) -> str:
    lines: list[str] = []
    lines.append(_c(1, f"=== Selection: {result.filename} ==="))
    lines.append(
        f"  Selected : {result.total_selected}  "
        f"Excluded : {result.total_excluded}"
    )
    if not result.selected:
        lines.append(_c(33, "  (no entries matched)"))
    else:
        lines.append(_c(36, "  Matched entries:"))
        for entry in result.selected:
            val = entry.value or ""
            lines.append(f"    {_c(32, entry.key)} = {val}")
    return "\n".join(lines)


def format_selection_summary(result: SelectionResult) -> str:
    total = result.total_selected + result.total_excluded
    pct = (
        round(100 * result.total_selected / total)
        if total > 0 else 0
    )
    status = _c(32, "OK") if result.total_selected > 0 else _c(33, "EMPTY")
    return (
        f"[{status}] {result.filename}: "
        f"{result.total_selected}/{total} entries selected ({pct}%)"
    )

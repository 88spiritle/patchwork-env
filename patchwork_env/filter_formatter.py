"""Format FilterResult objects for terminal output."""
from __future__ import annotations

from patchwork_env.env_filter import FilterResult


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_filter_result(result: FilterResult) -> str:
    lines: list[str] = []
    header = _c(1, f"Filter results — {result.filename}")
    lines.append(header)

    criteria = result.criteria
    if criteria.key_pattern:
        lines.append(f"  Key pattern  : {_c(36, criteria.key_pattern)}")
    if criteria.value_pattern:
        lines.append(f"  Value pattern: {_c(36, criteria.value_pattern)}")
    if criteria.exclude_empty:
        lines.append(f"  Exclude empty: {_c(33, 'yes')}")
    if criteria.invert:
        lines.append(f"  Inverted     : {_c(33, 'yes')}")

    lines.append("")

    if not result.matched:
        lines.append(_c(33, "  (no entries matched)"))
    else:
        for entry in result.matched:
            key_str = _c(32, entry.key)
            val_str = entry.value or _c(90, "<empty>")
            lines.append(f"  {key_str} = {val_str}")

    return "\n".join(lines)


def format_filter_summary(result: FilterResult) -> str:
    status = _c(32, "✔") if result.total_matched else _c(33, "–")
    return (
        f"{status} {result.filename}: "
        f"{result.total_matched} matched, "
        f"{result.total_excluded} excluded "
        f"(of {result.total_input} total)"
    )

"""Formatter for PadResult output."""
from __future__ import annotations

from patchwork_env.env_padder import PadResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_pad_result(result: PadResult) -> str:
    lines = []
    label = result.filename or "<unknown>"
    lines.append(_c("1;34", f"Padded: {label}"))
    lines.append(_c("90", f"  Key width : {result.width}"))
    lines.append(_c("90", f"  Entries   : {result.total_entries}"))

    if not result.lines:
        lines.append(_c("90", "  (no entries)"))
        return "\n".join(lines)

    lines.append("")
    for pl in result.lines:
        lines.append(f"  {pl.padded_text}")

    return "\n".join(lines)


def format_pad_summary(result: PadResult) -> str:
    label = result.filename or "<unknown>"
    status = (
        _c("32", "already aligned")
        if result.was_already_aligned
        else _c("33", "re-aligned")
    )
    return (
        f"{_c('1', label)}: "
        f"{result.total_entries} entries, "
        f"width={result.width} "
        f"[{status}]"
    )

"""Formatter for DeduplicateResult."""
from __future__ import annotations

from patchwork_env.env_deduplicator import DeduplicateResult


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_dedup_result(result: DeduplicateResult) -> str:
    lines = []
    header = f"Deduplication report — {result.filename or '(unknown)'}"
    lines.append(_c("1;36", header))
    lines.append(_c("90", "-" * len(header)))

    if not result.records:
        lines.append(_c("32", "  ✔ No duplicate keys found."))
        return "\n".join(lines)

    for rec in result.records:
        lines.append(
            f"  {_c('33', rec.key)}: kept line {_c('32', str(rec.kept.line_number))}, "
            f"removed {_c('31', str(len(rec.discarded)))} duplicate(s) "
            f"(lines {[e.line_number for e in rec.discarded]})"
        )

    return "\n".join(lines)


def format_dedup_summary(result: DeduplicateResult) -> str:
    if result.total_removed == 0:
        status = _c("32", "clean")
        detail = "no duplicates removed"
    else:
        status = _c("31", "duplicates found")
        detail = (
            f"{result.total_removed} entr{'y' if result.total_removed == 1 else 'ies'} "
            f"removed across {len(result.records)} key(s)"
        )
    name = result.filename or "(unknown)"
    return f"{_c('1', name)} — {status}: {detail}"

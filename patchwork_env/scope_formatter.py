"""Formatter for ScopeResult output."""
from __future__ import annotations

from patchwork_env.env_scope import ScopeResult


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_scope_result(result: ScopeResult) -> str:
    lines: list[str] = []
    lines.append(_c(1, f"Scope: {result.scope}  [{result.filename}]"))
    lines.append(
        f"  Included: {result.total_included}  "
        f"Excluded: {result.total_excluded}"
    )
    if result.included:
        lines.append(_c(32, "  Included keys:"))
        for entry in result.included:
            lines.append(f"    + {entry.key} = {entry.value}")
    if result.excluded:
        lines.append(_c(33, "  Excluded keys:"))
        for entry in result.excluded:
            label = entry.key if entry.key else "<blank>"
            lines.append(f"    - {label}")
    return "\n".join(lines)


def format_scope_summary(result: ScopeResult) -> str:
    status = _c(32, "OK") if result.total_included > 0 else _c(31, "EMPTY")
    return (
        f"[scope] {result.scope} | {result.filename} | "
        f"in={result.total_included} out={result.total_excluded} | {status}"
    )

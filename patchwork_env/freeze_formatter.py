"""Formatting helpers for FreezeRegistry results."""
from __future__ import annotations

from typing import List

from patchwork_env.env_freezer import FreezeResult, FrozenKey


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_frozen_key(fk: FrozenKey) -> str:
    reason = f"  # {fk.reason}" if fk.reason else ""
    return f"  {_c('96', fk.key)} = {_c('93', fk.frozen_value)}{reason}"


def format_freeze_result(result: FreezeResult, filename: str = "") -> str:
    lines: List[str] = []
    header = _c("1;94", "=== Freeze Report ===")
    if filename:
        header += f"  [{_c('90', filename)}]"
    lines.append(header)

    if not result.frozen_keys:
        lines.append(_c("90", "  No frozen keys applied."))
        return "\n".join(lines)

    lines.append(_c("1", f"  Frozen keys enforced: {result.total_frozen}"))
    for fk in result.frozen_keys:
        marker = _c("91", " [overridden]") if fk.key in result.skipped_keys else ""
        lines.append(format_frozen_key(fk) + marker)

    if result.skipped_keys:
        lines.append("")
        lines.append(_c("91", f"  Values overridden: {result.total_skipped}"))
        for k in result.skipped_keys:
            lines.append(f"    {_c('91', k)}: incoming value was replaced with frozen value")

    return "\n".join(lines)


def format_freeze_summary(frozen: List[FrozenKey]) -> str:
    if not frozen:
        return _c("90", "No keys are currently frozen.")
    lines = [_c("1;94", "Frozen keys:")]
    for fk in frozen:
        lines.append(format_frozen_key(fk))
    return "\n".join(lines)

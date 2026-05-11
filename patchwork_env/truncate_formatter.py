"""Format TruncateResult objects for terminal output."""
from __future__ import annotations

from patchwork_env.env_truncator import TruncateResult


def _c(code: int, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_truncate_result(result: TruncateResult, max_length: int = 80) -> str:
    lines: list[str] = []
    header = _c(1, f"Truncate report — {result.filename}  (max={max_length})")
    lines.append(header)
    lines.append("-" * 60)

    for rec in result.records:
        if rec.was_truncated:
            key_str = _c(33, rec.key)
            val_str = _c(90, rec.truncated_value + "…")
            tag = _c(31, "[TRUNCATED]")
            lines.append(f"  {key_str} = {val_str}  {tag}")
        else:
            key_str = _c(32, rec.key)
            val_str = rec.truncated_value
            lines.append(f"  {key_str} = {val_str}")

    lines.append("-" * 60)
    if result.was_clean:
        lines.append(_c(32, "✔ No values exceeded the length limit."))
    else:
        lines.append(
            _c(33, f"⚠ {result.total_truncated} value(s) were truncated.")
        )
    return "\n".join(lines)


def format_truncate_summary(result: TruncateResult) -> str:
    status = "clean" if result.was_clean else f"{result.total_truncated} truncated"
    return f"{result.filename}: {status} ({len(result.records)} keys)"

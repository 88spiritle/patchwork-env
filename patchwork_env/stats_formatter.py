"""Format DiffStats reports for terminal output."""
from __future__ import annotations

from patchwork_env.env_differ_stats import DiffStats, KeyStat


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_key_stat(stat: KeyStat) -> str:
    parts = []
    if stat.added:
        parts.append(_c("32", f"+{stat.added}"))
    if stat.removed:
        parts.append(_c("31", f"-{stat.removed}"))
    if stat.modified:
        parts.append(_c("33", f"~{stat.modified}"))
    change_str = "  ".join(parts) if parts else _c("90", "no changes")
    return f"  {_c('1', stat.key):<40} {change_str}"


def format_stats(ds: DiffStats, top: int = 0) -> str:
    lines: list[str] = []
    lines.append(_c("1;34", f"Diff Statistics — {ds.filename}"))
    lines.append(_c("90", f"  {ds.total_events} total change events across {len(ds.stats)} key(s)"))
    lines.append("")

    entries = ds.most_changed
    if top > 0:
        entries = entries[:top]

    if not entries:
        lines.append(_c("90", "  (no changes recorded)"))
    else:
        lines.append(_c("4", f"  {'Key':<38}  Changes"))
        for stat in entries:
            lines.append(format_key_stat(stat))

    return "\n".join(lines)


def format_stats_summary(ds: DiffStats) -> str:
    return (
        f"Stats [{ds.filename}]: "
        f"{len(ds.stats)} key(s), "
        f"{ds.total_events} event(s)"
    )

"""Format snapshot diff reports for human-readable output."""
from __future__ import annotations

from patchwork_env.snapshot_diff import SnapshotDiffReport

_RESET = "\033[0m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _c(color: str, text: str, use_color: bool) -> str:
    return f"{color}{text}{_RESET}" if use_color else text


def format_snapshot_diff(report: SnapshotDiffReport, use_color: bool = True) -> str:
    lines = []
    old_ts = report.old_snapshot.captured_at
    new_ts = report.new_snapshot.captured_at
    env = report.new_snapshot.environment

    lines.append(_c(_BOLD, f"Snapshot diff — environment: {env}", use_color))
    lines.append(f"  from : {old_ts}  ({report.old_snapshot.filepath})")
    lines.append(f"  to   : {new_ts}  ({report.new_snapshot.filepath})")
    lines.append("")

    if not report.has_changes():
        lines.append("  No changes detected.")
        return "\n".join(lines)

    for entry in report.added:
        lines.append(_c(_GREEN, f"  + {entry.key}={entry.new_value}", use_color))

    for entry in report.removed:
        lines.append(_c(_RED, f"  - {entry.key}={entry.old_value}", use_color))

    for entry in report.modified:
        lines.append(_c(_YELLOW, f"  ~ {entry.key}", use_color))
        lines.append(_c(_RED,    f"      old: {entry.old_value}", use_color))
        lines.append(_c(_GREEN,  f"      new: {entry.new_value}", use_color))

    return "\n".join(lines)


def format_snapshot_summary(report: SnapshotDiffReport) -> str:
    return (
        f"Snapshot summary [{report.new_snapshot.environment}]: "
        f"+{len(report.added)} added, "
        f"-{len(report.removed)} removed, "
        f"~{len(report.modified)} modified, "
        f"={len(report.unchanged)} unchanged"
    )

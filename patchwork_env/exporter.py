"""Export snapshots and diffs to portable formats (JSON, dotenv text)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from patchwork_env.snapshot import Snapshot
    from patchwork_env.snapshot_diff import SnapshotDiffReport


def export_snapshot_json(snapshot: "Snapshot", indent: int = 2) -> str:
    """Serialise a Snapshot to a JSON string."""
    return json.dumps(snapshot.to_dict(), indent=indent)


def export_snapshot_dotenv(snapshot: "Snapshot") -> str:
    """Render a Snapshot back to .env file text.

    Comments and blank lines from the original file are not preserved;
    only key=value pairs are emitted, one per line.
    """
    lines: list[str] = []
    for entry in snapshot.entries:
        if entry.comment:
            lines.append(f"# {entry.comment}")
        lines.append(f"{entry.key}={entry.raw_value}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_diff_json(report: "SnapshotDiffReport", indent: int = 2) -> str:
    """Serialise a SnapshotDiffReport to a JSON string."""
    payload = {
        "environment": report.environment,
        "added": [e.key for e in report.added],
        "removed": [e.key for e in report.removed],
        "modified": [
            {"key": e.key, "old": e.old_value, "new": e.new_value}
            for e in report.modified
        ],
        "unchanged": [e.key for e in report.unchanged],
    }
    return json.dumps(payload, indent=indent)


def export_diff_patch(report: "SnapshotDiffReport") -> str:
    """Render a SnapshotDiffReport as a unified-style patch text.

    Lines prefixed with '+' are additions, '-' are removals, and '~'
    indicates a modified value (shows old then new).
    """
    lines: list[str] = []
    header = f"# patchwork-env diff — {report.environment}"
    lines.append(header)
    lines.append("#" * len(header))

    for entry in report.added:
        lines.append(f"+ {entry.key}={entry.new_value}")
    for entry in report.removed:
        lines.append(f"- {entry.key}={entry.old_value}")
    for entry in report.modified:
        lines.append(f"- {entry.key}={entry.old_value}")
        lines.append(f"+ {entry.key}={entry.new_value}")

    return "\n".join(lines) + "\n"

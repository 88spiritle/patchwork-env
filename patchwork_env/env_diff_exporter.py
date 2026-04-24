"""env_diff_exporter.py — Export enriched diff reports to multiple formats.

Supports exporting a SnapshotDiffReport to JSON, Markdown, and CSV so that
diff results can be consumed by external CI pipelines or stored as artefacts.
"""

from __future__ import annotations

import csv
import io
import json
from typing import List

from patchwork_env.snapshot_diff import SnapshotDiffEntry, SnapshotDiffReport


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def export_snapshot_diff_json(report: SnapshotDiffReport, *, indent: int = 2) -> str:
    """Serialise *report* to a JSON string.

    Each entry carries ``key``, ``status``, ``old_value``, and ``new_value``
    so that downstream tools can process the diff without re-parsing .env files.
    """
    entries: List[dict] = []
    for entry in report.entries:
        entries.append({
            "key": entry.key,
            "status": entry.status.value,
            "old_value": entry.old_value,
            "new_value": entry.new_value,
        })

    payload = {
        "old_label": report.old_label,
        "new_label": report.new_label,
        "total_added": len(report.added),
        "total_removed": len(report.removed),
        "total_modified": len(report.modified),
        "total_unchanged": len(report.unchanged),
        "entries": entries,
    }
    return json.dumps(payload, indent=indent)


# ---------------------------------------------------------------------------
# Markdown export
# ---------------------------------------------------------------------------

def export_snapshot_diff_markdown(report: SnapshotDiffReport) -> str:
    """Render *report* as a GitHub-flavoured Markdown table.

    Useful for posting diff summaries as pull-request comments or wiki pages.
    """
    lines: List[str] = []
    lines.append(f"## Env Diff: `{report.old_label}` → `{report.new_label}`\n")
    lines.append(
        f"**Added:** {len(report.added)}  "
        f"**Removed:** {len(report.removed)}  "
        f"**Modified:** {len(report.modified)}  "
        f"**Unchanged:** {len(report.unchanged)}\n"
    )

    if not report.entries:
        lines.append("_No differences detected._\n")
        return "\n".join(lines)

    lines.append("| Key | Status | Old Value | New Value |")
    lines.append("|-----|--------|-----------|-----------|")

    status_icons = {
        "added": "✅ added",
        "removed": "❌ removed",
        "modified": "✏️ modified",
        "unchanged": "· unchanged",
    }

    for entry in sorted(report.entries, key=lambda e: e.key):
        icon = status_icons.get(entry.status.value, entry.status.value)
        old_val = entry.old_value if entry.old_value is not None else "—"
        new_val = entry.new_value if entry.new_value is not None else "—"
        lines.append(f"| `{entry.key}` | {icon} | `{old_val}` | `{new_val}` |")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def export_snapshot_diff_csv(report: SnapshotDiffReport) -> str:
    """Serialise *report* to CSV text (RFC 4180).

    Columns: ``key``, ``status``, ``old_value``, ``new_value``.
    Missing values are represented as empty strings.
    """
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["key", "status", "old_value", "new_value"])

    for entry in sorted(report.entries, key=lambda e: e.key):
        writer.writerow([
            entry.key,
            entry.status.value,
            entry.old_value if entry.old_value is not None else "",
            entry.new_value if entry.new_value is not None else "",
        ])

    return buf.getvalue()

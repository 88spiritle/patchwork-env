"""Formatter for VersionHistory and VersionEntry objects."""
from __future__ import annotations

from patchwork_env.env_version import VersionEntry, VersionHistory


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_version_entry(entry: VersionEntry) -> str:
    lines = []
    tag = _c(f"v{entry.version}", "36;1")
    label = _c(entry.label, "33")
    lines.append(f"  {tag}  {label}")
    lines.append(f"      file      : {entry.filename}")
    lines.append(f"      keys      : {entry.key_count}")
    lines.append(f"      timestamp : {entry.timestamp}")
    if entry.notes:
        lines.append(f"      notes     : {entry.notes}")
    return "\n".join(lines)


def format_version_history(history: VersionHistory) -> str:
    header = _c(f"Version History — {history.name}", "1")
    lines = [header, ""]
    if not history.entries:
        lines.append(_c("  (no versions recorded)", "2"))
    else:
        for entry in reversed(history.entries):
            lines.append(format_version_entry(entry))
            lines.append("")
    return "\n".join(lines).rstrip()


def format_version_summary(history: VersionHistory) -> str:
    count = len(history.entries)
    latest = history.latest()
    if latest is None:
        return _c(f"{history.name}: no versions", "2")
    label = _c(latest.label, "33")
    ver = _c(f"v{latest.version}", "36;1")
    return f"{history.name}: {count} version(s), latest {ver} ({label})"

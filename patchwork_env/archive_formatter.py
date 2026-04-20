"""Format archive listings and entries for CLI output."""

from __future__ import annotations

from patchwork_env.env_archiver import Archive, ArchiveEntry


def _c(code: str, text: str) -> str:
    codes = {"cyan": "\033[36m", "green": "\033[32m", "yellow": "\033[33m", "reset": "\033[0m", "bold": "\033[1m"}
    return f"{codes.get(code, '')}{text}{codes['reset']}"


def format_archive_entry(entry: ArchiveEntry) -> str:
    lines = [
        f"  {_c('bold', entry.label)}  ({_c('cyan', entry.timestamp)})",
        f"    file   : {entry.snapshot.filename}",
        f"    keys   : {len(entry.snapshot.entries)}",
    ]
    return "\n".join(lines)


def format_archive(archive: Archive) -> str:
    if not archive.entries:
        return _c("yellow", f"Archive '{archive.name}' is empty.")

    header = _c("bold", f"Archive: {archive.name}  ({len(archive.entries)} snapshot(s))")
    rows = []
    for idx, entry in enumerate(archive.entries, 1):
        rows.append(f"[{idx}] " + format_archive_entry(entry))

    return "\n".join([header, ""] + rows)


def format_archive_summary(archive: Archive) -> str:
    latest = archive.latest()
    if latest is None:
        return f"Archive '{archive.name}': no snapshots recorded."
    return (
        f"Archive '{archive.name}': {len(archive.entries)} snapshot(s). "
        f"Latest: {_c('green', latest.label)} @ {latest.timestamp}"
    )

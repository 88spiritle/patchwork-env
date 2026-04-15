"""Compare two snapshots and produce a structured diff report."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from patchwork_env.snapshot import Snapshot


@dataclass
class SnapshotDiffEntry:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    status: str  # "added", "removed", "modified", "unchanged"

    def __repr__(self) -> str:
        return f"<SnapshotDiffEntry key={self.key!r} status={self.status}>"


@dataclass
class SnapshotDiffReport:
    old_snapshot: Snapshot
    new_snapshot: Snapshot
    entries: List[SnapshotDiffEntry]

    @property
    def added(self) -> List[SnapshotDiffEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[SnapshotDiffEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def modified(self) -> List[SnapshotDiffEntry]:
        return [e for e in self.entries if e.status == "modified"]

    @property
    def unchanged(self) -> List[SnapshotDiffEntry]:
        return [e for e in self.entries if e.status == "unchanged"]

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiffReport:
    """Produce a SnapshotDiffReport between two snapshots."""
    old_map = old.entry_map()
    new_map = new.entry_map()
    all_keys = sorted(set(old_map) | set(new_map))

    entries: List[SnapshotDiffEntry] = []
    for key in all_keys:
        if key not in old_map:
            entries.append(SnapshotDiffEntry(key=key, old_value=None, new_value=new_map[key], status="added"))
        elif key not in new_map:
            entries.append(SnapshotDiffEntry(key=key, old_value=old_map[key], new_value=None, status="removed"))
        elif old_map[key] != new_map[key]:
            entries.append(SnapshotDiffEntry(key=key, old_value=old_map[key], new_value=new_map[key], status="modified"))
        else:
            entries.append(SnapshotDiffEntry(key=key, old_value=old_map[key], new_value=new_map[key], status="unchanged"))

    return SnapshotDiffReport(old_snapshot=old, new_snapshot=new, entries=entries)

"""Compute per-key change frequency statistics across multiple diffs."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable

from patchwork_env.differ import EnvDiff, DiffStatus


@dataclass
class KeyStat:
    key: str
    added: int = 0
    removed: int = 0
    modified: int = 0

    @property
    def total_changes(self) -> int:
        return self.added + self.removed + self.modified

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"KeyStat(key={self.key!r}, added={self.added}, "
            f"removed={self.removed}, modified={self.modified})"
        )


@dataclass
class DiffStats:
    filename: str
    stats: dict[str, KeyStat] = field(default_factory=dict)

    @property
    def most_changed(self) -> list[KeyStat]:
        """Return KeyStats sorted by total_changes descending."""
        return sorted(self.stats.values(), key=lambda s: s.total_changes, reverse=True)

    @property
    def total_events(self) -> int:
        return sum(s.total_changes for s in self.stats.values())

    def __repr__(self) -> str:  # pragma: no cover
        return f"DiffStats(filename={self.filename!r}, keys={len(self.stats)})"


def compute_stats(diffs: Iterable[EnvDiff], filename: str = "<aggregate>") -> DiffStats:
    """Aggregate change counts across an iterable of EnvDiff objects."""
    result = DiffStats(filename=filename)

    for diff in diffs:
        for entry in diff.entries:
            key = entry.key
            if key not in result.stats:
                result.stats[key] = KeyStat(key=key)
            stat = result.stats[key]
            if entry.status == DiffStatus.ADDED:
                stat.added += 1
            elif entry.status == DiffStatus.REMOVED:
                stat.removed += 1
            elif entry.status == DiffStatus.MODIFIED:
                stat.modified += 1

    return result

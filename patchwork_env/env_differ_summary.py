"""Summarise cross-environment diff statistics for multiple file pairs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.differ import EnvDiff, DiffStatus


@dataclass
class EnvDiffSummary:
    """Aggregated statistics across one or more EnvDiff objects."""

    names: List[str] = field(default_factory=list)
    total_added: int = 0
    total_removed: int = 0
    total_modified: int = 0
    total_unchanged: int = 0

    @property
    def total_changes(self) -> int:
        return self.total_added + self.total_removed + self.total_modified

    @property
    def total_keys(self) -> int:
        return self.total_changes + self.total_unchanged

    @property
    def change_ratio(self) -> float:
        """Fraction of keys that changed (0.0 – 1.0)."""
        if self.total_keys == 0:
            return 0.0
        return self.total_changes / self.total_keys

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"EnvDiffSummary(pairs={len(self.names)}, "
            f"added={self.total_added}, removed={self.total_removed}, "
            f"modified={self.total_modified}, unchanged={self.total_unchanged})"
        )


def summarise_diffs(diffs: List[EnvDiff]) -> EnvDiffSummary:
    """Collapse a list of EnvDiff objects into a single summary."""
    summary = EnvDiffSummary()
    for diff in diffs:
        summary.names.append(f"{diff.base_name} → {diff.target_name}")
        for entry in diff.entries:
            if entry.status == DiffStatus.ADDED:
                summary.total_added += 1
            elif entry.status == DiffStatus.REMOVED:
                summary.total_removed += 1
            elif entry.status == DiffStatus.MODIFIED:
                summary.total_modified += 1
            else:
                summary.total_unchanged += 1
    return summary

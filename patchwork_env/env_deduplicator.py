"""Deduplication: identify and remove duplicate keys, keeping a chosen occurrence."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from patchwork_env.parser import EnvEntry


class KeepPolicy(str, Enum):
    FIRST = "first"
    LAST = "last"


@dataclass
class DeduplicateRecord:
    key: str
    kept: EnvEntry
    discarded: List[EnvEntry] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DeduplicateRecord(key={self.key!r}, kept_line={self.kept.line_number}, "
            f"discarded={[e.line_number for e in self.discarded]})"
        )


@dataclass
class DeduplicateResult:
    filename: str
    records: List[DeduplicateRecord] = field(default_factory=list)
    clean_entries: List[EnvEntry] = field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return sum(len(r.discarded) for r in self.records)

    @property
    def affected_keys(self) -> List[str]:
        return [r.key for r in self.records]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DeduplicateResult(filename={self.filename!r}, "
            f"total_removed={self.total_removed})"
        )


def deduplicate(
    entries: List[EnvEntry],
    filename: str = "",
    policy: KeepPolicy = KeepPolicy.LAST,
) -> DeduplicateResult:
    """Return a DeduplicateResult with duplicates resolved per *policy*."""
    seen: Dict[str, List[EnvEntry]] = {}
    for entry in entries:
        if entry.key is None:
            continue
        seen.setdefault(entry.key, []).append(entry)

    records: List[DeduplicateRecord] = []
    kept_entries: Dict[str, EnvEntry] = {}

    for key, occurrences in seen.items():
        if len(occurrences) == 1:
            kept_entries[key] = occurrences[0]
            continue
        keeper = occurrences[-1] if policy == KeepPolicy.LAST else occurrences[0]
        discarded = [e for e in occurrences if e is not keeper]
        records.append(DeduplicateRecord(key=key, kept=keeper, discarded=discarded))
        kept_entries[key] = keeper

    # Preserve original order using the kept entry positions.
    clean = [e for e in entries if e.key is None or kept_entries.get(e.key) is e]
    return DeduplicateResult(filename=filename, records=records, clean_entries=clean)

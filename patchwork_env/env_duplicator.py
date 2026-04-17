"""Detect and report duplicate keys within a parsed .env file."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry


@dataclass
class DuplicateGroup:
    key: str
    occurrences: List[EnvEntry]

    def __repr__(self) -> str:  # pragma: no cover
        return f"DuplicateGroup(key={self.key!r}, count={len(self.occurrences)})"


@dataclass
class DuplicateReport:
    filename: str
    groups: List[DuplicateGroup] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.groups) > 0

    @property
    def duplicate_keys(self) -> List[str]:
        return [g.key for g in self.groups]


def find_duplicates(entries: List[EnvEntry], filename: str = "<unknown>") -> DuplicateReport:
    """Return a DuplicateReport listing every key that appears more than once."""
    counts: Counter = Counter(e.key for e in entries if e.key is not None)
    groups: List[DuplicateGroup] = []
    for key, count in counts.items():
        if count > 1:
            occurrences = [e for e in entries if e.key == key]
            groups.append(DuplicateGroup(key=key, occurrences=occurrences))
    groups.sort(key=lambda g: g.key)
    return DuplicateReport(filename=filename, groups=groups)

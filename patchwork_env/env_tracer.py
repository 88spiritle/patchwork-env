"""Trace the origin of env keys across multiple source files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class TraceRecord:
    """Records which source file(s) defined a given key."""

    key: str
    sources: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"TraceRecord(key={self.key!r}, sources={self.sources})"

    @property
    def is_unique(self) -> bool:
        """True when the key appears in exactly one source."""
        return len(self.sources) == 1

    @property
    def is_conflicted(self) -> bool:
        """True when the key appears in multiple sources with differing values."""
        return len(set(self.values)) > 1


@dataclass
class TraceReport:
    """Aggregated trace results for a set of env files."""

    file_names: List[str]
    records: Dict[str, TraceRecord] = field(default_factory=dict)

    @property
    def conflicted_keys(self) -> List[str]:
        return [k for k, r in self.records.items() if r.is_conflicted]

    @property
    def unique_keys(self) -> List[str]:
        return [k for k, r in self.records.items() if r.is_unique]

    def get(self, key: str) -> Optional[TraceRecord]:
        return self.records.get(key.upper())


def trace_entries(
    sources: Dict[str, List[EnvEntry]],
) -> TraceReport:
    """Build a TraceReport from a mapping of filename -> entries.

    Parameters
    ----------
    sources:
        Ordered dict of ``{filename: [EnvEntry, ...]}``.  The order
        determines which value is considered the "last writer wins" value
        when keys overlap.
    """
    report = TraceReport(file_names=list(sources.keys()))

    for filename, entries in sources.items():
        for entry in entries:
            if entry.key is None:
                continue
            upper = entry.key.upper()
            if upper not in report.records:
                report.records[upper] = TraceRecord(key=upper)
            record = report.records[upper]
            record.sources.append(filename)
            record.values.append(entry.value or "")

    return report

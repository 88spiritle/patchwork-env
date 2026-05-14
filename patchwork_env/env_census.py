"""env_census.py – aggregate key/value statistics across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from patchwork_env.parser import EnvEntry


@dataclass
class CensusRow:
    """Statistics for a single key observed across one or more files."""

    key: str
    occurrences: int
    unique_values: List[str]
    sources: List[str]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CensusRow(key={self.key!r}, occurrences={self.occurrences}, "
            f"unique_values={len(self.unique_values)}, sources={self.sources})"
        )

    @property
    def is_consistent(self) -> bool:
        """True when all occurrences share the same value."""
        return len(self.unique_values) <= 1


@dataclass
class CensusReport:
    """Full census across all supplied env files."""

    filenames: List[str]
    rows: List[CensusRow] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.rows)

    @property
    def inconsistent_keys(self) -> List[CensusRow]:
        return [r for r in self.rows if not r.is_consistent]

    @property
    def consistent_keys(self) -> List[CensusRow]:
        return [r for r in self.rows if r.is_consistent]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CensusReport(files={len(self.filenames)}, "
            f"total_keys={self.total_keys}, "
            f"inconsistent={len(self.inconsistent_keys)})"
        )


def build_census(
    env_groups: Sequence[tuple[str, Sequence[EnvEntry]]]
) -> CensusReport:
    """Build a CensusReport from multiple (filename, entries) pairs."""
    filenames = [name for name, _ in env_groups]
    key_map: Dict[str, Dict[str, list]] = {}

    for filename, entries in env_groups:
        for entry in entries:
            if entry.key is None:
                continue
            k = entry.key.upper()
            if k not in key_map:
                key_map[k] = {"values": [], "sources": []}
            key_map[k]["values"].append(entry.value or "")
            key_map[k]["sources"].append(filename)

    rows = [
        CensusRow(
            key=k,
            occurrences=len(v["sources"]),
            unique_values=list(dict.fromkeys(v["values"])),
            sources=v["sources"],
        )
        for k, v in sorted(key_map.items())
    ]
    return CensusReport(filenames=filenames, rows=rows)

"""Trim leading/trailing whitespace from env entry values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry


@dataclass
class TrimRecord:
    """Records a single trimmed entry."""
    key: str
    original_value: str
    trimmed_value: str

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TrimRecord(key={self.key!r}, "
            f"original={self.original_value!r}, "
            f"trimmed={self.trimmed_value!r})"
        )


@dataclass
class TrimResult:
    """Result of trimming a collection of env entries."""
    filename: str
    entries: List[EnvEntry]
    records: List[TrimRecord] = field(default_factory=list)

    @property
    def total_trimmed(self) -> int:
        return len(self.records)

    @property
    def was_clean(self) -> bool:
        return self.total_trimmed == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TrimResult(filename={self.filename!r}, "
            f"total_trimmed={self.total_trimmed})"
        )


def trim_entries(entries: List[EnvEntry], filename: str = "<unknown>") -> TrimResult:
    """Return a TrimResult with whitespace stripped from all values.

    Blank lines and comments are passed through unchanged.
    """
    trimmed_entries: List[EnvEntry] = []
    records: List[TrimRecord] = []

    for entry in entries:
        if entry.key is None:
            trimmed_entries.append(entry)
            continue

        original = entry.value
        cleaned = original.strip() if original is not None else original

        if cleaned != original:
            records.append(TrimRecord(key=entry.key, original_value=original, trimmed_value=cleaned))
            entry = EnvEntry(
                key=entry.key,
                value=cleaned,
                raw_line=entry.raw_line,
                comment=entry.comment,
            )

        trimmed_entries.append(entry)

    return TrimResult(filename=filename, entries=trimmed_entries, records=records)

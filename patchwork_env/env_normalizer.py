"""Normalize .env entry keys and values to a canonical form."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from patchwork_env.parser import EnvEntry


@dataclass
class NormalizeRecord:
    """Record of a single normalization action applied to an entry."""

    key: str
    original_key: str
    original_value: str
    normalized_key: str
    normalized_value: str
    changes: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        changes = ", ".join(self.changes) or "none"
        return f"NormalizeRecord(key={self.key!r}, changes=[{changes}])"


@dataclass
class NormalizeResult:
    """Result of normalizing a collection of entries."""

    filename: str
    records: List[NormalizeRecord] = field(default_factory=list)
    entries: List[EnvEntry] = field(default_factory=list)

    @property
    def total_changed(self) -> int:
        return sum(1 for r in self.records if r.changes)

    @property
    def was_clean(self) -> bool:
        return self.total_changed == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"NormalizeResult(filename={self.filename!r}, "
            f"total_changed={self.total_changed})"
        )


def normalize_entries(
    entries: Sequence[EnvEntry],
    filename: str = "<unknown>",
    *,
    uppercase_keys: bool = True,
    strip_value_whitespace: bool = True,
) -> NormalizeResult:
    """Return a NormalizeResult with each entry normalized.

    Parameters
    ----------
    entries:
        Source entries to normalize.
    filename:
        Label used in the result (e.g. the .env file path).
    uppercase_keys:
        When *True*, key names are coerced to upper-case.
    strip_value_whitespace:
        When *True*, leading/trailing whitespace is stripped from values.
    """
    records: List[NormalizeRecord] = []
    normalized: List[EnvEntry] = []

    for entry in entries:
        changes: List[str] = []
        new_key = entry.key
        new_value = entry.value

        if uppercase_keys and entry.key != entry.key.upper():
            new_key = entry.key.upper()
            changes.append("key_uppercased")

        if strip_value_whitespace and entry.value != entry.value.strip():
            new_value = entry.value.strip()
            changes.append("value_stripped")

        record = NormalizeRecord(
            key=new_key,
            original_key=entry.key,
            original_value=entry.value,
            normalized_key=new_key,
            normalized_value=new_value,
            changes=changes,
        )
        records.append(record)

        new_entry = EnvEntry(
            key=new_key,
            value=new_value,
            comment=entry.comment,
            raw_line=entry.raw_line,
        )
        normalized.append(new_entry)

    return NormalizeResult(filename=filename, records=records, entries=normalized)

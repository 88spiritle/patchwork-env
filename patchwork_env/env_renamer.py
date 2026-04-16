"""Rename keys across an env entry list, tracking changes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from patchwork_env.parser import EnvEntry


@dataclass
class RenameRecord:
    old_key: str
    new_key: str
    value: str

    def __repr__(self) -> str:
        return f"RenameRecord({self.old_key!r} -> {self.new_key!r})"


@dataclass
class RenameResult:
    entries: List[EnvEntry]
    records: List[RenameRecord] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def renamed_keys(self) -> List[str]:
        return [r.old_key for r in self.records]


def rename_key(
    entries: List[EnvEntry],
    old_key: str,
    new_key: str,
) -> RenameResult:
    """Return a new entry list with old_key renamed to new_key."""
    records: List[RenameRecord] = []
    skipped: List[str] = []
    updated: List[EnvEntry] = []

    found = False
    for entry in entries:
        if entry.key == old_key:
            if new_key in {e.key for e in entries if e.key}:
                skipped.append(old_key)
                updated.append(entry)
            else:
                records.append(RenameRecord(old_key, new_key, entry.value))
                updated.append(
                    EnvEntry(
                        key=new_key,
                        value=entry.value,
                        comment=entry.comment,
                        raw=entry.raw,
                    )
                )
                found = True
        else:
            updated.append(entry)

    if not found and old_key not in skipped:
        skipped.append(old_key)

    return RenameResult(entries=updated, records=records, skipped=skipped)


def rename_many(
    entries: List[EnvEntry],
    mapping: dict,
) -> RenameResult:
    """Apply multiple renames sequentially from {old: new} mapping."""
    result = RenameResult(entries=list(entries))
    for old_key, new_key in mapping.items():
        partial = rename_key(result.entries, old_key, new_key)
        result.entries = partial.entries
        result.records.extend(partial.records)
        result.skipped.extend(partial.skipped)
    return result

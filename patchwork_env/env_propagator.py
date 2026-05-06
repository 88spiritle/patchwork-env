"""Propagate key-value pairs from a source env to one or more target envs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class PropagationRecord:
    """Records the outcome of propagating a single key to a target file."""

    key: str
    target_file: str
    old_value: Optional[str]  # None when the key did not exist in target
    new_value: str
    overwritten: bool

    def __repr__(self) -> str:  # pragma: no cover
        status = "overwritten" if self.overwritten else "added"
        return f"<PropagationRecord {self.key!r} -> {self.target_file!r} [{status}]>"


@dataclass
class PropagationResult:
    """Aggregated result of a propagation run."""

    source_file: str
    records: List[PropagationRecord] = field(default_factory=list)

    @property
    def total_propagated(self) -> int:
        return len(self.records)

    @property
    def total_overwritten(self) -> int:
        return sum(1 for r in self.records if r.overwritten)

    @property
    def total_added(self) -> int:
        return sum(1 for r in self.records if not r.overwritten)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<PropagationResult source={self.source_file!r} "
            f"propagated={self.total_propagated}>"
        )


def propagate(
    source_entries: List[EnvEntry],
    target_entries: List[EnvEntry],
    target_file: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> PropagationResult:
    """Propagate *keys* from *source_entries* into *target_entries*.

    Parameters
    ----------
    source_entries:
        Parsed entries from the source .env file.
    target_entries:
        Parsed entries from the target .env file (mutated in-place).
    target_file:
        Display name / path of the target file (used in records).
    keys:
        Explicit list of keys to propagate.  When *None* all keys from the
        source are propagated.
    overwrite:
        When *True* existing keys in the target are overwritten.  When
        *False* only keys absent from the target are added.
    """
    source_map = {e.key: e for e in source_entries if e.key is not None}
    target_map = {e.key: e for e in target_entries if e.key is not None}

    keys_to_propagate = list(keys) if keys is not None else list(source_map.keys())

    result = PropagationResult(source_file=getattr(source_entries[0], "source", "source") if source_entries else "source")

    for key in keys_to_propagate:
        if key not in source_map:
            continue
        src_entry = source_map[key]
        existing = target_map.get(key)

        if existing is not None and not overwrite:
            continue

        old_value = existing.value if existing is not None else None
        record = PropagationRecord(
            key=key,
            target_file=target_file,
            old_value=old_value,
            new_value=src_entry.value,
            overwritten=existing is not None,
        )
        result.records.append(record)

        if existing is not None:
            existing.value = src_entry.value
        else:
            target_entries.append(
                EnvEntry(
                    key=src_entry.key,
                    value=src_entry.value,
                    comment=src_entry.comment,
                    raw=src_entry.raw,
                )
            )
            target_map[key] = target_entries[-1]

    return result

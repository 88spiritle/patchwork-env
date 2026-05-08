"""env_cloner.py — Clone entries from one environment to another with optional key transformation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class CloneRecord:
    source_key: str
    target_key: str
    value: str
    overwritten: bool = False

    def __repr__(self) -> str:  # pragma: no cover
        tag = "overwrite" if self.overwritten else "new"
        return f"CloneRecord({self.source_key!r} -> {self.target_key!r}, {tag})"


@dataclass
class CloneResult:
    source_filename: str
    target_filename: str
    records: List[CloneRecord] = field(default_factory=list)

    @property
    def total_cloned(self) -> int:
        return len(self.records)

    @property
    def total_overwritten(self) -> int:
        return sum(1 for r in self.records if r.overwritten)

    @property
    def was_clean(self) -> bool:
        return self.total_overwritten == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CloneResult(cloned={self.total_cloned}, "
            f"overwritten={self.total_overwritten})"
        )


def clone_entries(
    source: List[EnvEntry],
    target: List[EnvEntry],
    source_filename: str = "source.env",
    target_filename: str = "target.env",
    keys: Optional[List[str]] = None,
    key_transform: Optional[Callable[[str], str]] = None,
    overwrite: bool = True,
) -> CloneResult:
    """Clone entries from *source* into *target*.

    Args:
        source: Entries to copy from.
        target: Existing entries in the destination file.
        source_filename: Label for the source file.
        target_filename: Label for the target file.
        keys: If provided, only clone entries whose key is in this list.
        key_transform: Optional callable to rename keys during cloning.
        overwrite: When True, existing keys in target are overwritten.

    Returns:
        A CloneResult describing what was copied.
    """
    target_map: dict[str, EnvEntry] = {e.key: e for e in target}
    result = CloneResult(
        source_filename=source_filename,
        target_filename=target_filename,
    )

    for entry in source:
        if keys is not None and entry.key not in keys:
            continue
        target_key = key_transform(entry.key) if key_transform else entry.key
        already_exists = target_key in target_map
        if already_exists and not overwrite:
            continue
        record = CloneRecord(
            source_key=entry.key,
            target_key=target_key,
            value=entry.value,
            overwritten=already_exists,
        )
        result.records.append(record)
        target_map[target_key] = EnvEntry(
            key=target_key,
            value=entry.value,
            raw_line=f"{target_key}={entry.value}",
        )

    return result

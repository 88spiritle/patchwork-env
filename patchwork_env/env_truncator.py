"""Truncate long env values to a maximum character length."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry

DEFAULT_MAX_LENGTH = 80


@dataclass
class TruncateRecord:
    key: str
    original_value: str
    truncated_value: str
    was_truncated: bool

    def __repr__(self) -> str:  # pragma: no cover
        flag = "*" if self.was_truncated else ""
        return f"TruncateRecord({self.key}{flag})"


@dataclass
class TruncateResult:
    filename: str
    records: List[TruncateRecord] = field(default_factory=list)

    @property
    def total_truncated(self) -> int:
        return sum(1 for r in self.records if r.was_truncated)

    @property
    def was_clean(self) -> bool:
        return self.total_truncated == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TruncateResult(filename={self.filename!r}, "
            f"truncated={self.total_truncated}/{len(self.records)})"
        )


def truncate_entries(
    entries: List[EnvEntry],
    filename: str = "",
    max_length: int = DEFAULT_MAX_LENGTH,
) -> TruncateResult:
    """Return a TruncateResult with values clipped to *max_length* characters."""
    result = TruncateResult(filename=filename)
    for entry in entries:
        original = entry.value
        if len(original) > max_length:
            truncated = original[:max_length]
            was_truncated = True
        else:
            truncated = original
            was_truncated = False
        result.records.append(
            TruncateRecord(
                key=entry.key,
                original_value=original,
                truncated_value=truncated,
                was_truncated=was_truncated,
            )
        )
    return result

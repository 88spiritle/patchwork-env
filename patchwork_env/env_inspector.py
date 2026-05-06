"""Inspect an env file and produce a structured summary of its contents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry


@dataclass
class InspectionReport:
    filename: str
    total_keys: int
    blank_lines: int
    comment_lines: int
    empty_values: List[str] = field(default_factory=list)
    duplicate_keys: List[str] = field(default_factory=list)
    longest_key: str = ""
    longest_value_key: str = ""

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"InspectionReport(filename={self.filename!r}, "
            f"total_keys={self.total_keys}, "
            f"blank_lines={self.blank_lines}, "
            f"comment_lines={self.comment_lines})"
        )

    @property
    def has_empty_values(self) -> bool:
        return len(self.empty_values) > 0

    @property
    def has_duplicates(self) -> bool:
        return len(self.duplicate_keys) > 0


def inspect_entries(
    entries: List[EnvEntry],
    filename: str = "<unknown>",
    raw_lines: List[str] | None = None,
) -> InspectionReport:
    """Analyse *entries* and return an :class:`InspectionReport`."""
    raw_lines = raw_lines or []

    blank_lines = sum(1 for ln in raw_lines if ln.strip() == "")
    comment_lines = sum(1 for ln in raw_lines if ln.strip().startswith("#"))

    seen: dict[str, int] = {}
    empty_values: List[str] = []
    longest_key = ""
    longest_value_key = ""
    longest_val_len = -1

    for entry in entries:
        key = entry.key
        seen[key] = seen.get(key, 0) + 1

        if entry.value == "":
            empty_values.append(key)

        if len(key) > len(longest_key):
            longest_key = key

        val_len = len(entry.value)
        if val_len > longest_val_len:
            longest_val_len = val_len
            longest_value_key = key

    duplicate_keys = [k for k, count in seen.items() if count > 1]

    return InspectionReport(
        filename=filename,
        total_keys=len(entries),
        blank_lines=blank_lines,
        comment_lines=comment_lines,
        empty_values=empty_values,
        duplicate_keys=duplicate_keys,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
    )

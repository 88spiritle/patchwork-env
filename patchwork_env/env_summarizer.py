"""Summarize an env file into high-level statistics and metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry


@dataclass
class EnvSummary:
    filename: str
    total_keys: int
    empty_values: int
    commented_lines: int
    unique_prefixes: List[str] = field(default_factory=list)
    longest_key: str = ""
    longest_value_key: str = ""

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"EnvSummary(filename={self.filename!r}, total_keys={self.total_keys}, "
            f"empty_values={self.empty_values})"
        )


def _extract_prefix(key: str) -> str:
    """Return the prefix segment before the first underscore, or the full key."""
    parts = key.split("_", 1)
    return parts[0] if len(parts) > 1 else key


def summarize(entries: List[EnvEntry], filename: str = "") -> EnvSummary:
    """Build an EnvSummary from a list of EnvEntry objects."""
    if not entries:
        return EnvSummary(
            filename=filename,
            total_keys=0,
            empty_values=0,
            commented_lines=0,
        )

    empty = sum(1 for e in entries if e.value == "")
    commented = sum(1 for e in entries if getattr(e, "comment", None) is not None)
    prefixes = sorted(set(_extract_prefix(e.key) for e in entries))

    longest_key = max(entries, key=lambda e: len(e.key)).key
    longest_value_key = max(entries, key=lambda e: len(e.value)).key

    return EnvSummary(
        filename=filename,
        total_keys=len(entries),
        empty_values=empty,
        commented_lines=commented,
        unique_prefixes=prefixes,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
    )

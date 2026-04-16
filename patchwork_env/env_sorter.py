"""Sort and group .env file entries by key, prefix, or custom order."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from patchwork_env.parser import EnvEntry


class SortMode(str, Enum):
    ALPHABETICAL = "alpha"
    REVERSE = "reverse"
    BY_PREFIX = "prefix"
    PRESERVE = "preserve"


def _key_prefix(entry: EnvEntry) -> str:
    """Return the prefix of a key (part before the first underscore)."""
    if "_" in entry.key:
        return entry.key.split("_", 1)[0]
    return entry.key


def sort_entries(
    entries: List[EnvEntry],
    mode: SortMode = SortMode.ALPHABETICAL,
    custom_order: Optional[List[str]] = None,
) -> List[EnvEntry]:
    """Return a new list of entries sorted according to *mode*.

    Args:
        entries: The entries to sort.
        mode: Sorting strategy to apply.
        custom_order: When *mode* is BY_PREFIX, use this list to define
            the desired prefix order.  Unknown prefixes sort last.

    Returns:
        A new sorted list; the original list is not mutated.
    """
    if mode is SortMode.PRESERVE:
        return list(entries)

    if mode is SortMode.ALPHABETICAL:
        return sorted(entries, key=lambda e: e.key)

    if mode is SortMode.REVERSE:
        return sorted(entries, key=lambda e: e.key, reverse=True)

    if mode is SortMode.BY_PREFIX:
        order = {p: i for i, p in enumerate(custom_order or [])}
        max_idx = len(order)

        def _sort_key(e: EnvEntry):
            prefix = _key_prefix(e)
            return (order.get(prefix, max_idx), e.key)

        return sorted(entries, key=_sort_key)

    raise ValueError(f"Unknown sort mode: {mode}")


def group_by_prefix(entries: List[EnvEntry]) -> dict[str, List[EnvEntry]]:
    """Group entries by their key prefix (segment before the first '_')."""
    groups: dict[str, List[EnvEntry]] = {}
    for entry in entries:
        prefix = _key_prefix(entry)
        groups.setdefault(prefix, []).append(entry)
    return groups

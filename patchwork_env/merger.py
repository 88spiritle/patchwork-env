"""Merge resolved diffs back into an EnvFile, producing a reconciled result."""

from __future__ import annotations

from typing import List

from patchwork_env.parser import EnvEntry, EnvFile
from patchwork_env.resolver import Resolution, ResolutionStrategy


def merge(base: EnvFile, resolution: Resolution) -> EnvFile:
    """Apply a Resolution to a base EnvFile and return the merged EnvFile.

    Rules:
    - KEEP_BASE   → keep the base value unchanged.
    - USE_TARGET  → overwrite with the target value (or add if missing in base).
    - REMOVE      → drop the key from the output entirely.
    - SKIP        → leave the key as-is in base (same as KEEP_BASE for existing keys;
                    for added keys, the key is omitted because it was not chosen).
    """
    base_dict = {entry.key: entry for entry in base.entries}
    result_entries: List[EnvEntry] = []

    # Track keys we have already handled so we can append new keys at the end.
    handled: set[str] = set()

    for diff_entry in resolution.diff.entries:
        key = diff_entry.key
        handled.add(key)
        strategy = resolution.strategies.get(key, ResolutionStrategy.KEEP_BASE)

        if strategy == ResolutionStrategy.REMOVE:
            continue

        if strategy == ResolutionStrategy.USE_TARGET:
            if diff_entry.target_value is not None:
                result_entries.append(
                    EnvEntry(
                        key=key,
                        value=diff_entry.target_value,
                        comment=base_dict[key].comment if key in base_dict else None,
                        raw_line=None,
                    )
                )
            # If target_value is None the key was removed on target side; skip.
            continue

        # KEEP_BASE or SKIP: retain the base entry if it exists.
        if key in base_dict:
            result_entries.append(base_dict[key])

    # Preserve base entries that were not part of any diff (identical keys).
    for entry in base.entries:
        if entry.key not in handled:
            result_entries.append(entry)

    return EnvFile(path=base.path, entries=result_entries)


def merge_to_text(base: EnvFile, resolution: Resolution) -> str:
    """Return the merged EnvFile serialised as .env text."""
    merged = merge(base, resolution)
    lines: List[str] = []
    for entry in merged.entries:
        if entry.comment:
            lines.append(f"{entry.key}={entry.value}  # {entry.comment}")
        else:
            lines.append(f"{entry.key}={entry.value}")
    return "\n".join(lines)

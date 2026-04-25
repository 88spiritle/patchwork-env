"""Flatten nested or prefixed env entries into a canonical flat structure."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class FlattenedEntry:
    original_key: str
    flat_key: str
    value: str
    source_file: str
    prefix_stripped: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        tag = f" (stripped: {self.prefix_stripped!r})" if self.prefix_stripped else ""
        return f"FlattenedEntry({self.flat_key!r}={self.value!r}{tag})"


@dataclass
class FlattenResult:
    source_file: str
    entries: List[FlattenedEntry] = field(default_factory=list)
    prefix_used: Optional[str] = None

    @property
    def flat_keys(self) -> List[str]:
        return [e.flat_key for e in self.entries]

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def total_stripped(self) -> int:
        return sum(1 for e in self.entries if e.prefix_stripped is not None)


def flatten_entries(
    entries: List[EnvEntry],
    source_file: str,
    strip_prefix: Optional[str] = None,
    uppercase: bool = False,
) -> FlattenResult:
    """Flatten a list of EnvEntry objects.

    Args:
        entries: Parsed env entries.
        source_file: Label for the source file.
        strip_prefix: If provided, remove this prefix (case-insensitive) from keys.
        uppercase: Normalise all flat keys to upper-case.

    Returns:
        A FlattenResult containing FlattenedEntry items.
    """
    result = FlattenResult(source_file=source_file, prefix_used=strip_prefix)
    norm_prefix = strip_prefix.upper() if strip_prefix else None

    for entry in entries:
        if entry.key is None:
            continue

        original_key = entry.key
        flat_key = original_key
        prefix_stripped: Optional[str] = None

        if norm_prefix and flat_key.upper().startswith(norm_prefix):
            prefix_stripped = flat_key[: len(norm_prefix)]
            flat_key = flat_key[len(norm_prefix):].lstrip("_")

        if uppercase:
            flat_key = flat_key.upper()

        result.entries.append(
            FlattenedEntry(
                original_key=original_key,
                flat_key=flat_key,
                value=entry.value or "",
                source_file=source_file,
                prefix_stripped=prefix_stripped,
            )
        )

    return result

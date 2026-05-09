"""Count and categorise entries in a .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry


@dataclass
class CountBreakdown:
    """Aggregated counts for a parsed .env file."""

    filename: str
    total: int = 0
    with_values: int = 0
    empty_values: int = 0
    commented_out: int = 0
    unique_prefixes: int = 0
    _prefixes: List[str] = field(default_factory=list, repr=False)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CountBreakdown(file={self.filename!r}, total={self.total}, "
            f"with_values={self.with_values}, empty={self.empty_values})"
        )


def _extract_prefix(key: str) -> str:
    """Return the portion of *key* before the first underscore (or the full key)."""
    return key.split("_")[0].upper() if "_" in key else key.upper()


def count_entries(
    entries: List[EnvEntry],
    filename: str = "<unknown>",
    *,
    commented_lines: int = 0,
) -> CountBreakdown:
    """Build a :class:`CountBreakdown` from a list of parsed entries.

    Parameters
    ----------
    entries:
        Parsed :class:`~patchwork_env.parser.EnvEntry` objects.
    filename:
        Label used in the breakdown (typically the file path).
    commented_lines:
        Number of comment / blank lines encountered during parsing that are
        not represented in *entries*.
    """
    breakdown = CountBreakdown(filename=filename)
    breakdown.total = len(entries)
    breakdown.commented_out = commented_lines

    prefixes: set[str] = set()
    for entry in entries:
        if entry.value:
            breakdown.with_values += 1
        else:
            breakdown.empty_values += 1
        prefixes.add(_extract_prefix(entry.key))

    breakdown._prefixes = sorted(prefixes)
    breakdown.unique_prefixes = len(prefixes)
    return breakdown

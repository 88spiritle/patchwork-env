"""Filter .env entries by key pattern, value pattern, or category."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence

from patchwork_env.parser import EnvEntry


@dataclass
class FilterCriteria:
    """Criteria used to filter env entries."""
    key_pattern: Optional[str] = None
    value_pattern: Optional[str] = None
    exclude_empty: bool = False
    invert: bool = False

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FilterCriteria(key={self.key_pattern!r}, "
            f"value={self.value_pattern!r}, "
            f"exclude_empty={self.exclude_empty}, invert={self.invert})"
        )


@dataclass
class FilterResult:
    """Result of applying filter criteria to a list of entries."""
    filename: str
    criteria: FilterCriteria
    matched: List[EnvEntry] = field(default_factory=list)
    total_input: int = 0

    @property
    def total_matched(self) -> int:
        return len(self.matched)

    @property
    def total_excluded(self) -> int:
        return self.total_input - self.total_matched

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FilterResult(filename={self.filename!r}, "
            f"matched={self.total_matched}/{self.total_input})"
        )


def _make_predicate(criteria: FilterCriteria) -> Callable[[EnvEntry], bool]:
    key_re = re.compile(criteria.key_pattern, re.IGNORECASE) if criteria.key_pattern else None
    val_re = re.compile(criteria.value_pattern, re.IGNORECASE) if criteria.value_pattern else None

    def predicate(entry: EnvEntry) -> bool:
        if key_re and not key_re.search(entry.key):
            return False
        if val_re and not val_re.search(entry.value or ""):
            return False
        if criteria.exclude_empty and not (entry.value or "").strip():
            return False
        return True

    return predicate


def filter_entries(
    entries: Sequence[EnvEntry],
    criteria: FilterCriteria,
    filename: str = "<unknown>",
) -> FilterResult:
    """Apply *criteria* to *entries* and return a FilterResult."""
    predicate = _make_predicate(criteria)
    matched = [
        e for e in entries
        if (not criteria.invert and predicate(e))
        or (criteria.invert and not predicate(e))
    ]
    return FilterResult(
        filename=filename,
        criteria=criteria,
        matched=matched,
        total_input=len(entries),
    )

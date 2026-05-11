from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import re

from patchwork_env.parser import EnvEntry


@dataclass
class SearchCriteria:
    key_pattern: Optional[str] = None
    value_pattern: Optional[str] = None
    case_sensitive: bool = False

    def __repr__(self) -> str:
        return (
            f"SearchCriteria(key={self.key_pattern!r}, "
            f"value={self.value_pattern!r}, "
            f"case_sensitive={self.case_sensitive})"
        )


@dataclass
class SearchHit:
    entry: EnvEntry
    matched_key: bool
    matched_value: bool

    def __repr__(self) -> str:
        flags = []
        if self.matched_key:
            flags.append("key")
        if self.matched_value:
            flags.append("value")
        return f"SearchHit({self.entry.key!r}, matched={flags})"


@dataclass
class SearchResult:
    filename: str
    criteria: SearchCriteria
    hits: List[SearchHit] = field(default_factory=list)

    @property
    def total_hits(self) -> int:
        return len(self.hits)

    @property
    def hit_keys(self) -> List[str]:
        return [h.entry.key for h in self.hits]

    def __repr__(self) -> str:
        return f"SearchResult({self.filename!r}, hits={self.total_hits})"


def search_entries(
    entries: List[EnvEntry],
    criteria: SearchCriteria,
    filename: str = "",
) -> SearchResult:
    flags = 0 if criteria.case_sensitive else re.IGNORECASE
    key_re = re.compile(criteria.key_pattern, flags) if criteria.key_pattern else None
    val_re = re.compile(criteria.value_pattern, flags) if criteria.value_pattern else None

    hits: List[SearchHit] = []
    for entry in entries:
        mk = bool(key_re and key_re.search(entry.key))
        mv = bool(val_re and val_re.search(entry.value or ""))
        if key_re and val_re:
            if mk and mv:
                hits.append(SearchHit(entry, mk, mv))
        elif key_re:
            if mk:
                hits.append(SearchHit(entry, mk, False))
        elif val_re:
            if mv:
                hits.append(SearchHit(entry, False, mv))
        else:
            hits.append(SearchHit(entry, False, False))

    return SearchResult(filename=filename, criteria=criteria, hits=hits)

"""Track and report deprecated keys in .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DeprecationRecord:
    key: str
    reason: Optional[str] = None
    replacement: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        parts = [f"key={self.key!r}"]
        if self.reason:
            parts.append(f"reason={self.reason!r}")
        if self.replacement:
            parts.append(f"replacement={self.replacement!r}")
        return f"DeprecationRecord({', '.join(parts)})"

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "reason": self.reason,
            "replacement": self.replacement,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DeprecationRecord":
        return cls(
            key=data["key"],
            reason=data.get("reason"),
            replacement=data.get("replacement"),
        )


@dataclass
class DeprecationHit:
    key: str
    record: DeprecationRecord

    def __repr__(self) -> str:  # pragma: no cover
        return f"DeprecationHit(key={self.key!r})"


@dataclass
class DeprecationReport:
    filename: str
    hits: List[DeprecationHit] = field(default_factory=list)

    @property
    def has_deprecated(self) -> bool:
        return len(self.hits) > 0

    @property
    def deprecated_keys(self) -> List[str]:
        return [h.key for h in self.hits]


class DeprecationRegistry:
    def __init__(self) -> None:
        self._records: dict[str, DeprecationRecord] = {}

    def register(self, key: str, reason: Optional[str] = None, replacement: Optional[str] = None) -> DeprecationRecord:
        record = DeprecationRecord(key=key.upper(), reason=reason, replacement=replacement)
        self._records[key.upper()] = record
        return record

    def unregister(self, key: str) -> None:
        self._records.pop(key.upper(), None)

    def is_deprecated(self, key: str) -> bool:
        return key.upper() in self._records

    def get(self, key: str) -> Optional[DeprecationRecord]:
        return self._records.get(key.upper())

    def scan(self, entries: list, filename: str = "<unknown>") -> DeprecationReport:
        hits = []
        for entry in entries:
            record = self.get(entry.key)
            if record is not None:
                hits.append(DeprecationHit(key=entry.key, record=record))
        return DeprecationReport(filename=filename, hits=hits)

    def all_records(self) -> List[DeprecationRecord]:
        return list(self._records.values())

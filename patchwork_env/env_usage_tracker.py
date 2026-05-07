"""Track which env keys have been accessed/used across environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class UsageRecord:
    key: str
    source_file: str
    accessed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    access_count: int = 1

    def __repr__(self) -> str:  # pragma: no cover
        return f"UsageRecord(key={self.key!r}, file={self.source_file!r}, count={self.access_count})"

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "source_file": self.source_file,
            "accessed_at": self.accessed_at,
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UsageRecord":
        return cls(
            key=data["key"],
            source_file=data["source_file"],
            accessed_at=data["accessed_at"],
            access_count=data["access_count"],
        )


@dataclass
class UsageReport:
    source_file: str
    records: List[UsageRecord] = field(default_factory=list)

    @property
    def total_tracked(self) -> int:
        return len(self.records)

    @property
    def unused_keys(self) -> List[str]:
        return [r.key for r in self.records if r.access_count == 0]

    @property
    def most_used(self) -> Optional[UsageRecord]:
        if not self.records:
            return None
        return max(self.records, key=lambda r: r.access_count)

    def get(self, key: str) -> Optional[UsageRecord]:
        key = key.upper()
        for r in self.records:
            if r.key == key:
                return r
        return None


class UsageTracker:
    def __init__(self) -> None:
        self._records: Dict[str, UsageRecord] = {}

    def track(self, key: str, source_file: str) -> UsageRecord:
        key = key.upper()
        if key in self._records:
            self._records[key].access_count += 1
        else:
            self._records[key] = UsageRecord(key=key, source_file=source_file)
        return self._records[key]

    def untrack(self, key: str) -> None:
        self._records.pop(key.upper(), None)

    def report(self, source_file: str) -> UsageReport:
        return UsageReport(
            source_file=source_file,
            records=list(self._records.values()),
        )

    def reset(self) -> None:
        self._records.clear()

"""env_expiry.py — track and report expiring or expired env keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass
class ExpiryRecord:
    key: str
    expires_on: date
    reason: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return f"ExpiryRecord(key={self.key!r}, expires_on={self.expires_on}, reason={self.reason!r})"

    def is_expired(self, today: Optional[date] = None) -> bool:
        today = today or datetime.utcnow().date()
        return self.expires_on <= today

    def days_until(self, today: Optional[date] = None) -> int:
        today = today or datetime.utcnow().date()
        return (self.expires_on - today).days

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "expires_on": self.expires_on.isoformat(),
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExpiryRecord":
        return cls(
            key=data["key"],
            expires_on=date.fromisoformat(data["expires_on"]),
            reason=data.get("reason"),
        )


@dataclass
class ExpiryReport:
    filename: str
    records: List[ExpiryRecord] = field(default_factory=list)

    @property
    def expired(self) -> List[ExpiryRecord]:
        return [r for r in self.records if r.is_expired()]

    @property
    def expiring_soon(self, within_days: int = 30) -> List[ExpiryRecord]:
        return [
            r for r in self.records
            if not r.is_expired() and r.days_until() <= within_days
        ]

    @property
    def has_expired(self) -> bool:
        return len(self.expired) > 0


def build_expiry_report(filename: str, registry: List[ExpiryRecord]) -> ExpiryReport:
    """Return an ExpiryReport for the given registry."""
    return ExpiryReport(filename=filename, records=list(registry))

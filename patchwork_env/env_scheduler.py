"""env_scheduler.py — schedule time-based activation of env variable overrides."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class ScheduledOverride:
    """A single key/value override active within [start, end)."""

    key: str
    value: str
    start: datetime
    end: Optional[datetime] = None  # None means "no expiry"
    label: str = ""

    def __repr__(self) -> str:  # pragma: no cover
        end_s = self.end.isoformat() if self.end else "∞"
        return (
            f"ScheduledOverride({self.key!r}, start={self.start.isoformat()}, "
            f"end={end_s}, label={self.label!r})"
        )

    def is_active(self, at: Optional[datetime] = None) -> bool:
        """Return True if the override is active at *at* (default: now)."""
        now = at or datetime.utcnow()
        if now < self.start:
            return False
        if self.end is not None and now >= self.end:
            return False
        return True


@dataclass
class Schedule:
    """Collection of scheduled overrides for a named environment."""

    name: str
    overrides: List[ScheduledOverride] = field(default_factory=list)

    def add(self, override: ScheduledOverride) -> ScheduledOverride:
        self.overrides.append(override)
        return override

    def remove(self, key: str) -> None:
        self.overrides = [o for o in self.overrides if o.key != key]

    def active_overrides(self, at: Optional[datetime] = None) -> List[ScheduledOverride]:
        """Return only the overrides that are currently active."""
        return [o for o in self.overrides if o.is_active(at)]

    def apply(self, entries: List[EnvEntry], at: Optional[datetime] = None) -> List[EnvEntry]:
        """Apply active overrides to *entries*, returning a new list."""
        active = {o.key: o.value for o in self.active_overrides(at)}
        result: List[EnvEntry] = []
        for entry in entries:
            if entry.key and entry.key in active:
                result.append(
                    EnvEntry(
                        key=entry.key,
                        value=active[entry.key],
                        comment=entry.comment,
                        raw=entry.raw,
                    )
                )
            else:
                result.append(entry)
        return result

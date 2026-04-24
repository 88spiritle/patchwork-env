"""env_locker.py – lock/unlock individual env keys to prevent accidental overwrite."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class LockedKey:
    key: str
    reason: Optional[str]
    locked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __repr__(self) -> str:  # pragma: no cover
        return f"LockedKey(key={self.key!r}, reason={self.reason!r})"

    def to_dict(self) -> dict:
        return {"key": self.key, "reason": self.reason, "locked_at": self.locked_at}

    @classmethod
    def from_dict(cls, data: dict) -> "LockedKey":
        obj = cls(key=data["key"], reason=data.get("reason"))
        obj.locked_at = data.get("locked_at", obj.locked_at)
        return obj


@dataclass
class LockRegistry:
    name: str
    _locks: dict = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------
    def lock(self, key: str, reason: Optional[str] = None) -> LockedKey:
        """Lock *key*; idempotent – re-locking updates the reason."""
        entry = LockedKey(key=key.upper(), reason=reason)
        self._locks[entry.key] = entry
        return entry

    def unlock(self, key: str) -> bool:
        """Remove lock for *key*. Returns True if a lock was removed."""
        return self._locks.pop(key.upper(), None) is not None

    def is_locked(self, key: str) -> bool:
        return key.upper() in self._locks

    def get(self, key: str) -> Optional[LockedKey]:
        return self._locks.get(key.upper())

    @property
    def locked_keys(self) -> List[LockedKey]:
        return list(self._locks.values())

    # ------------------------------------------------------------------
    def check_entries(self, entries: List[EnvEntry]) -> List[str]:
        """Return list of keys that are locked among *entries*."""
        return [e.key for e in entries if self.is_locked(e.key)]

    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "locks": [lk.to_dict() for lk in self._locks.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LockRegistry":
        reg = cls(name=data["name"])
        for item in data.get("locks", []):
            lk = LockedKey.from_dict(item)
            reg._locks[lk.key] = lk
        return reg

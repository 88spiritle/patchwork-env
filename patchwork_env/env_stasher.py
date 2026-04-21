"""Temporary stash for unsaved .env changes, similar to git stash."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class StashEntry:
    """A single stashed snapshot of env entries."""

    label: str
    entries: List[EnvEntry]
    stashed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"StashEntry(label={self.label!r}, "
            f"keys={len(self.entries)}, stashed_at={self.stashed_at!r})"
        )

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "stashed_at": self.stashed_at,
            "entries": [
                {"key": e.key, "value": e.value, "comment": e.comment}
                for e in self.entries
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StashEntry":
        entries = [
            EnvEntry(key=r["key"], value=r["value"], comment=r.get("comment", ""))
            for r in data["entries"]
        ]
        obj = cls(label=data["label"], entries=entries)
        obj.stashed_at = data["stashed_at"]
        return obj


@dataclass
class Stash:
    """Ordered collection of stash entries (newest first on pop)."""

    _entries: List[StashEntry] = field(default_factory=list)

    def push(self, label: str, entries: List[EnvEntry]) -> StashEntry:
        """Push a new stash entry and return it."""
        se = StashEntry(label=label, entries=list(entries))
        self._entries.append(se)
        return se

    def pop(self) -> Optional[StashEntry]:
        """Remove and return the most recently pushed entry, or None."""
        if not self._entries:
            return None
        return self._entries.pop()

    def peek(self) -> Optional[StashEntry]:
        """Return the most recent entry without removing it."""
        return self._entries[-1] if self._entries else None

    def drop(self, label: str) -> bool:
        """Remove a stash entry by label. Returns True if found."""
        for i, se in enumerate(self._entries):
            if se.label == label:
                del self._entries[i]
                return True
        return False

    def list(self) -> List[StashEntry]:
        """Return all stash entries, newest last."""
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

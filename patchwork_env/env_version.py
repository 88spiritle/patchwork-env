"""Version tracking for .env files across environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class VersionEntry:
    version: int
    label: str
    filename: str
    key_count: int
    timestamp: str
    notes: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"VersionEntry(v{self.version}, label={self.label!r}, "
            f"keys={self.key_count}, file={self.filename!r})"
        )

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "label": self.label,
            "filename": self.filename,
            "key_count": self.key_count,
            "timestamp": self.timestamp,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "VersionEntry":
        return cls(
            version=data["version"],
            label=data["label"],
            filename=data["filename"],
            key_count=data["key_count"],
            timestamp=data["timestamp"],
            notes=data.get("notes"),
        )


@dataclass
class VersionHistory:
    name: str
    entries: List[VersionEntry] = field(default_factory=list)

    def add(self, label: str, filename: str, key_count: int, notes: Optional[str] = None) -> VersionEntry:
        version = len(self.entries) + 1
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = VersionEntry(
            version=version,
            label=label,
            filename=filename,
            key_count=key_count,
            timestamp=timestamp,
            notes=notes,
        )
        self.entries.append(entry)
        return entry

    def latest(self) -> Optional[VersionEntry]:
        return self.entries[-1] if self.entries else None

    def get(self, version: int) -> Optional[VersionEntry]:
        for e in self.entries:
            if e.version == version:
                return e
        return None

    def to_dict(self) -> dict:
        return {"name": self.name, "entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict) -> "VersionHistory":
        history = cls(name=data["name"])
        history.entries = [VersionEntry.from_dict(e) for e in data.get("entries", [])]
        return history

"""Archive and restore snapshots of .env files with timestamped history."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from patchwork_env.snapshot import Snapshot


@dataclass
class ArchiveEntry:
    timestamp: str
    label: str
    snapshot: Snapshot

    def __repr__(self) -> str:
        return f"ArchiveEntry(label={self.label!r}, timestamp={self.timestamp!r})"

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "label": self.label,
            "snapshot": self.snapshot.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveEntry":
        return cls(
            timestamp=data["timestamp"],
            label=data["label"],
            snapshot=Snapshot.from_dict(data["snapshot"]),
        )


@dataclass
class Archive:
    name: str
    entries: List[ArchiveEntry] = field(default_factory=list)

    def add(self, snapshot: Snapshot, label: str = "") -> ArchiveEntry:
        ts = datetime.now(timezone.utc).isoformat()
        entry = ArchiveEntry(timestamp=ts, label=label or ts, snapshot=snapshot)
        self.entries.append(entry)
        return entry

    def latest(self) -> Optional[ArchiveEntry]:
        return self.entries[-1] if self.entries else None

    def find(self, label: str) -> Optional[ArchiveEntry]:
        for e in reversed(self.entries):
            if e.label == label:
                return e
        return None

    def to_dict(self) -> dict:
        return {"name": self.name, "entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict) -> "Archive":
        archive = cls(name=data["name"])
        archive.entries = [ArchiveEntry.from_dict(e) for e in data.get("entries", [])]
        return archive


def save_archive(archive: Archive, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(archive.to_dict(), fh, indent=2)


def load_archive(path: str) -> Archive:
    with open(path, "r", encoding="utf-8") as fh:
        return Archive.from_dict(json.load(fh))

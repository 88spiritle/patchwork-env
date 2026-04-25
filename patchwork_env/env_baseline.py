"""Baseline management: capture and compare a 'known-good' env state."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from patchwork_env.snapshot import Snapshot


@dataclass
class BaselineEntry:
    key: str
    value: str
    source: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"BaselineEntry(key={self.key!r}, source={self.source!r})"

    def to_dict(self) -> dict:
        return {"key": self.key, "value": self.value, "source": self.source}

    @classmethod
    def from_dict(cls, d: dict) -> "BaselineEntry":
        return cls(key=d["key"], value=d["value"], source=d["source"])


@dataclass
class Baseline:
    name: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    entries: List[BaselineEntry] = field(default_factory=list)

    # ------------------------------------------------------------------
    @property
    def entry_map(self) -> Dict[str, BaselineEntry]:
        return {e.key: e for e in self.entries}

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "created_at": self.created_at,
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Baseline":
        b = cls(name=d["name"], created_at=d["created_at"])
        b.entries = [BaselineEntry.from_dict(e) for e in d.get("entries", [])]
        return b


def capture_baseline(snapshot: Snapshot, name: str) -> Baseline:
    """Build a Baseline from an existing Snapshot."""
    b = Baseline(name=name)
    for entry in snapshot.entries:
        b.entries.append(
            BaselineEntry(key=entry.key, value=entry.value, source=snapshot.filename)
        )
    return b


@dataclass
class BaselineDrift:
    key: str
    baseline_value: Optional[str]
    current_value: Optional[str]
    status: str  # "added" | "removed" | "changed"

    def __repr__(self) -> str:  # pragma: no cover
        return f"BaselineDrift(key={self.key!r}, status={self.status!r})"


def detect_drift(baseline: Baseline, snapshot: Snapshot) -> List[BaselineDrift]:
    """Return keys that differ between a baseline and a current snapshot."""
    drifts: List[BaselineDrift] = []
    base_map = baseline.entry_map
    snap_map = {e.key: e for e in snapshot.entries}

    for key, be in base_map.items():
        if key not in snap_map:
            drifts.append(BaselineDrift(key, be.value, None, "removed"))
        elif snap_map[key].value != be.value:
            drifts.append(BaselineDrift(key, be.value, snap_map[key].value, "changed"))

    for key, se in snap_map.items():
        if key not in base_map:
            drifts.append(BaselineDrift(key, None, se.value, "added"))

    return sorted(drifts, key=lambda d: d.key)

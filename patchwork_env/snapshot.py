"""Snapshot module: capture and persist env file states for later comparison."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry, parse_env_file


@dataclass
class Snapshot:
    """A point-in-time capture of an env file."""

    environment: str
    filepath: str
    captured_at: str
    entries: List[Dict]

    @classmethod
    def capture(cls, filepath: str, environment: str) -> "Snapshot":
        entries = parse_env_file(filepath)
        return cls(
            environment=environment,
            filepath=filepath,
            captured_at=datetime.now(timezone.utc).isoformat(),
            entries=[{"key": e.key, "value": e.value, "comment": e.comment} for e in entries],
        )

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "Snapshot":
        return cls(
            environment=data["environment"],
            filepath=data["filepath"],
            captured_at=data["captured_at"],
            entries=data["entries"],
        )

    def entry_map(self) -> Dict[str, Optional[str]]:
        return {e["key"]: e["value"] for e in self.entries}


def save_snapshot(snapshot: Snapshot, store_dir: str) -> str:
    """Persist a snapshot as JSON. Returns the path written."""
    Path(store_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{snapshot.environment}_{ts}.json"
    dest = os.path.join(store_dir, filename)
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)
    return dest


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot.from_dict(data)


def list_snapshots(store_dir: str, environment: Optional[str] = None) -> List[str]:
    """Return sorted list of snapshot file paths, optionally filtered by env."""
    store = Path(store_dir)
    if not store.exists():
        return []
    files = sorted(store.glob("*.json"))
    if environment:
        files = [f for f in files if f.name.startswith(f"{environment}_")]
    return [str(f) for f in files]

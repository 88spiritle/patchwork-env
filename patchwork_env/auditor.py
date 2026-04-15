"""Audit trail for env diff and merge operations."""

from __future__ import annotations

import datetime
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class AuditEvent:
    timestamp: str
    operation: str          # 'diff' | 'merge' | 'validate'
    base_file: str
    target_file: Optional[str]
    summary: str
    details: dict = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        return f"AuditEvent(op={self.operation!r}, base={self.base_file!r})"


@dataclass
class AuditLog:
    events: List[AuditEvent] = field(default_factory=list)

    def record(self, event: AuditEvent) -> None:
        """Append an event to the log."""
        self.events.append(event)

    def to_dict(self) -> dict:
        return {"events": [asdict(e) for e in self.events]}

    @classmethod
    def from_dict(cls, data: dict) -> "AuditLog":
        log = cls()
        for raw in data.get("events", []):
            log.events.append(AuditEvent(**raw))
        return log

    def save(self, path: Path) -> None:
        """Persist the audit log as JSON."""
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> "AuditLog":
        """Load an audit log from a JSON file."""
        data = json.loads(path.read_text())
        return cls.from_dict(data)


def _now_iso() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def make_diff_event(
    base_file: str,
    target_file: str,
    added: int,
    removed: int,
    modified: int,
) -> AuditEvent:
    summary = f"+{added} -{removed} ~{modified}"
    return AuditEvent(
        timestamp=_now_iso(),
        operation="diff",
        base_file=base_file,
        target_file=target_file,
        summary=summary,
        details={"added": added, "removed": removed, "modified": modified},
    )


def make_merge_event(
    base_file: str,
    target_file: str,
    output_file: str,
    keys_written: int,
) -> AuditEvent:
    summary = f"merged {keys_written} keys -> {output_file}"
    return AuditEvent(
        timestamp=_now_iso(),
        operation="merge",
        base_file=base_file,
        target_file=target_file,
        summary=summary,
        details={"output_file": output_file, "keys_written": keys_written},
    )

"""env_changelog.py — Tracks and summarises changes between successive .env snapshots.

Builds a human-readable changelog from a sequence of SnapshotDiffReports so that
operators can audit the full history of environment mutations in one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from patchwork_env.snapshot_diff import SnapshotDiffReport, SnapshotDiffEntry


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ChangelogEntry:
    """A single versioned entry in the changelog."""

    version: int                          # monotonically increasing version number
    label: str                            # human-readable label, e.g. "v3" or a commit hash
    timestamp: datetime                   # when the change was recorded
    diff: SnapshotDiffReport              # the underlying diff that produced this entry
    note: Optional[str] = None           # optional free-text annotation

    def __repr__(self) -> str:  # pragma: no cover
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        added   = len(self.diff.added)
        removed = len(self.diff.removed)
        modified = len(self.diff.modified)
        return (
            f"<ChangelogEntry v{self.version} label={self.label!r} "
            f"+{added}/-{removed}/~{modified} at {ts}>"
        )

    def to_dict(self) -> dict:
        """Serialise to a plain dict for JSON export."""
        return {
            "version": self.version,
            "label": self.label,
            "timestamp": self.timestamp.isoformat(),
            "note": self.note,
            "changes": {
                "added":    [e.key for e in self.diff.added],
                "removed":  [e.key for e in self.diff.removed],
                "modified": [e.key for e in self.diff.modified],
                "unchanged": [e.key for e in self.diff.unchanged],
            },
        }


@dataclass
class Changelog:
    """Ordered collection of ChangelogEntry objects for a single .env file path."""

    filename: str
    entries: List[ChangelogEntry] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def record(
        self,
        diff: SnapshotDiffReport,
        label: Optional[str] = None,
        note: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> ChangelogEntry:
        """Append a new entry derived from *diff* and return it.

        Args:
            diff:      The SnapshotDiffReport that describes this change set.
            label:     Short human-readable identifier.  Defaults to ``"v<version>"``.
            note:      Optional free-text annotation stored on the entry.
            timestamp: Override the recorded time (defaults to *now* in UTC).

        Returns:
            The newly created :class:`ChangelogEntry`.
        """
        version = len(self.entries) + 1
        if label is None:
            label = f"v{version}"
        if timestamp is None:
            timestamp = datetime.now(tz=timezone.utc)

        entry = ChangelogEntry(
            version=version,
            label=label,
            timestamp=timestamp,
            diff=diff,
            note=note,
        )
        self.entries.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def latest(self) -> Optional[ChangelogEntry]:
        """Return the most recent entry, or *None* if the changelog is empty."""
        return self.entries[-1] if self.entries else None

    def since(self, version: int) -> List[ChangelogEntry]:
        """Return all entries with version *greater than* the given version number."""
        return [e for e in self.entries if e.version > version]

    def keys_ever_changed(self) -> List[str]:
        """Return a deduplicated, sorted list of every key touched across all entries."""
        seen: set[str] = set()
        for entry in self.entries:
            for diff_entry in (
                entry.diff.added
                + entry.diff.removed
                + entry.diff.modified
            ):
                seen.add(diff_entry.key)
        return sorted(seen)

    def to_dict(self) -> dict:
        """Serialise the full changelog to a plain dict."""
        return {
            "filename": self.filename,
            "total_versions": len(self.entries),
            "entries": [e.to_dict() for e in self.entries],
        }

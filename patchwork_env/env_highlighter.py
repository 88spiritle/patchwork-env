"""Highlight specific keys in an env file for review or export."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from patchwork_env.parser import EnvEntry


@dataclass
class HighlightRecord:
    entry: EnvEntry
    reason: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        tag = f" ({self.reason})" if self.reason else ""
        return f"<HighlightRecord key={self.entry.key!r}{tag}>"


@dataclass
class HighlightResult:
    filename: str
    highlighted: List[HighlightRecord] = field(default_factory=list)
    total_entries: int = 0

    @property
    def total_highlighted(self) -> int:
        return len(self.highlighted)

    @property
    def highlighted_keys(self) -> List[str]:
        return [r.entry.key for r in self.highlighted]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<HighlightResult file={self.filename!r} "
            f"highlighted={self.total_highlighted}/{self.total_entries}>"
        )


def highlight_entries(
    entries: Sequence[EnvEntry],
    keys: Sequence[str],
    filename: str = "<unknown>",
    reason: Optional[str] = None,
) -> HighlightResult:
    """Return a HighlightResult marking entries whose keys appear in *keys*."""
    normalised = {k.upper() for k in keys}
    records = [
        HighlightRecord(entry=e, reason=reason)
        for e in entries
        if e.key.upper() in normalised
    ]
    return HighlightResult(
        filename=filename,
        highlighted=records,
        total_entries=len(entries),
    )

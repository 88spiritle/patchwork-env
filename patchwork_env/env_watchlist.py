"""Watchlist: track specific keys of interest across environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class WatchedKey:
    key: str
    note: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        note_part = f", note={self.note!r}" if self.note else ""
        return f"WatchedKey(key={self.key!r}{note_part})"


@dataclass
class WatchHit:
    key: str
    entry: EnvEntry
    note: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return f"WatchHit(key={self.key!r}, value={self.entry.value!r})"


@dataclass
class WatchReport:
    filename: str
    hits: List[WatchHit] = field(default_factory=list)
    misses: List[str] = field(default_factory=list)

    @property
    def hit_keys(self) -> List[str]:
        return [h.key for h in self.hits]

    @property
    def miss_keys(self) -> List[str]:
        return list(self.misses)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"WatchReport(filename={self.filename!r}, "
            f"hits={len(self.hits)}, misses={len(self.misses)})"
        )


@dataclass
class Watchlist:
    _watched: Dict[str, WatchedKey] = field(default_factory=dict)

    def watch(self, key: str, note: Optional[str] = None) -> None:
        self._watched[key] = WatchedKey(key=key, note=note)

    def unwatch(self, key: str) -> None:
        self._watched.pop(key, None)

    def is_watched(self, key: str) -> bool:
        return key in self._watched

    @property
    def keys(self) -> List[str]:
        return list(self._watched.keys())

    def scan(self, entries: List[EnvEntry], filename: str = "<env>") -> WatchReport:
        entry_map = {e.key: e for e in entries}
        hits: List[WatchHit] = []
        misses: List[str] = []
        for key, watched in self._watched.items():
            if key in entry_map:
                hits.append(WatchHit(key=key, entry=entry_map[key], note=watched.note))
            else:
                misses.append(key)
        return WatchReport(filename=filename, hits=hits, misses=misses)

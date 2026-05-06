"""env_censor.py – selectively blank out env values based on a blocklist."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from patchwork_env.parser import EnvEntry

_DEFAULT_BLOCKLIST: tuple[str, ...] = (
    "PASSWORD", "PASSWD", "SECRET", "TOKEN",
    "API_KEY", "PRIVATE_KEY", "CREDENTIALS", "AUTH",
)


def is_censored_key(key: str, blocklist: Sequence[str] = _DEFAULT_BLOCKLIST) -> bool:
    """Return True if *key* matches any blocklist term (substring, case-insensitive)."""
    upper = key.upper()
    return any(term in upper for term in blocklist)


@dataclass
class CensoredEntry:
    original: EnvEntry
    censored: bool

    @property
    def key(self) -> str:
        return self.original.key

    @property
    def display_value(self) -> str:
        return "" if self.censored else self.original.value

    def __repr__(self) -> str:
        tag = "[CENSORED]" if self.censored else repr(self.display_value)
        return f"CensoredEntry(key={self.key!r}, value={tag})"


@dataclass
class CensorReport:
    filename: str
    entries: List[CensoredEntry] = field(default_factory=list)

    @property
    def censored_count(self) -> int:
        return sum(1 for e in self.entries if e.censored)

    @property
    def total(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:
        return (
            f"CensorReport(filename={self.filename!r}, "
            f"total={self.total}, censored={self.censored_count})"
        )


def censor_entries(
    entries: Sequence[EnvEntry],
    filename: str = "<unknown>",
    blocklist: Sequence[str] = _DEFAULT_BLOCKLIST,
) -> CensorReport:
    """Build a CensorReport blanking values whose keys match the blocklist."""
    results: List[CensoredEntry] = [
        CensoredEntry(original=e, censored=is_censored_key(e.key, blocklist))
        for e in entries
    ]
    return CensorReport(filename=filename, entries=results)

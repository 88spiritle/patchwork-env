"""Detect and report keys that have placeholder or stub values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry

_PLACEHOLDER_PATTERNS = (
    "CHANGEME",
    "REPLACE_ME",
    "TODO",
    "FIXME",
    "YOUR_",
    "<",
    ">",
    "...",
    "PLACEHOLDER",
    "EXAMPLE",
    "FILL_IN",
)


def is_placeholder(value: str) -> bool:
    """Return True if *value* looks like an unfilled placeholder."""
    upper = value.strip().upper()
    if not upper:
        return False
    return any(pat in upper for pat in _PLACEHOLDER_PATTERNS)


@dataclass
class PlaceholderHit:
    key: str
    value: str
    matched_pattern: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"PlaceholderHit(key={self.key!r}, pattern={self.matched_pattern!r})"


@dataclass
class PlaceholderReport:
    filename: str
    hits: List[PlaceholderHit] = field(default_factory=list)

    @property
    def has_placeholders(self) -> bool:
        return bool(self.hits)

    @property
    def placeholder_keys(self) -> List[str]:
        return [h.key for h in self.hits]

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PlaceholderReport(filename={self.filename!r}, "
            f"hits={len(self.hits)})"
        )


def scan_placeholders(
    entries: List[EnvEntry], filename: str = "<unknown>"
) -> PlaceholderReport:
    """Scan *entries* and return a :class:`PlaceholderReport`."""
    report = PlaceholderReport(filename=filename)
    for entry in entries:
        if entry.key is None:
            continue
        upper_val = (entry.value or "").strip().upper()
        for pat in _PLACEHOLDER_PATTERNS:
            if pat in upper_val:
                report.hits.append(
                    PlaceholderHit(
                        key=entry.key,
                        value=entry.value or "",
                        matched_pattern=pat,
                    )
                )
                break
    return report

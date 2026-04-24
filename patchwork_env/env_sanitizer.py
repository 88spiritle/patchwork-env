"""Sanitize .env entries by stripping dangerous or malformed values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry

_DANGEROUS_PATTERNS = (
    "$(",   # command substitution
    "`",    # backtick substitution
    "&&",   # shell chaining
    "||",   # shell chaining
    ";",    # statement separator
)


def _is_dangerous(value: str) -> bool:
    return any(pat in value for pat in _DANGEROUS_PATTERNS)


def _has_unmatched_quotes(value: str) -> bool:
    return value.count('"') % 2 != 0 or value.count("'") % 2 != 0


@dataclass
class SanitizeIssue:
    key: str
    reason: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"SanitizeIssue(key={self.key!r}, reason={self.reason!r})"


@dataclass
class SanitizeResult:
    filename: str
    clean: List[EnvEntry] = field(default_factory=list)
    issues: List[SanitizeIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def total_clean(self) -> int:
        return len(self.clean)

    @property
    def total_issues(self) -> int:
        return len(self.issues)


def sanitize_entries(entries: List[EnvEntry], filename: str = "") -> SanitizeResult:
    """Return a SanitizeResult separating clean entries from problematic ones."""
    result = SanitizeResult(filename=filename)
    for entry in entries:
        if entry.key is None:
            # blank lines / comments — pass through unchanged
            result.clean.append(entry)
            continue
        if _is_dangerous(entry.value):
            result.issues.append(
                SanitizeIssue(key=entry.key, reason="contains dangerous shell pattern")
            )
        elif _has_unmatched_quotes(entry.value):
            result.issues.append(
                SanitizeIssue(key=entry.key, reason="unmatched quotes in value")
            )
        else:
            result.clean.append(entry)
    return result

"""Redact sensitive values in .env entries before display or export."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Set

from patchwork_env.parser import EnvEntry

# Default patterns that indicate a key holds a sensitive value
_DEFAULT_SENSITIVE_PATTERNS: Set[str] = {
    "PASSWORD",
    "PASSWD",
    "SECRET",
    "TOKEN",
    "API_KEY",
    "PRIVATE_KEY",
    "AUTH",
    "CREDENTIALS",
    "DSN",
    "DATABASE_URL",
}

REDACTED_PLACEHOLDER = "***REDACTED***"


def is_sensitive(key: str, patterns: Set[str] | None = None) -> bool:
    """Return True if *key* matches any sensitive pattern (case-insensitive substring)."""
    check = patterns if patterns is not None else _DEFAULT_SENSITIVE_PATTERNS
    upper = key.upper()
    return any(pat in upper for pat in check)


@dataclass
class RedactedEntry:
    """An EnvEntry whose value may have been replaced with a placeholder."""

    key: str
    value: str
    redacted: bool
    original_entry: EnvEntry

    def __repr__(self) -> str:  # pragma: no cover
        flag = " [REDACTED]" if self.redacted else ""
        return f"RedactedEntry({self.key}={self.value!r}{flag})"


def redact_entries(
    entries: Iterable[EnvEntry],
    patterns: Set[str] | None = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> List[RedactedEntry]:
    """Return a list of RedactedEntry objects with sensitive values masked."""
    result: List[RedactedEntry] = []
    for entry in entries:
        if entry.key is None:
            continue
        sensitive = is_sensitive(entry.key, patterns)
        display_value = placeholder if sensitive else (entry.value or "")
        result.append(
            RedactedEntry(
                key=entry.key,
                value=display_value,
                redacted=sensitive,
                original_entry=entry,
            )
        )
    return result

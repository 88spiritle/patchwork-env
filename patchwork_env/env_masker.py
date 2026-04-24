"""env_masker.py – partial masking of sensitive env values for display."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry
from patchwork_env.env_redactor import is_sensitive

_DEFAULT_VISIBLE = 4
_MASK_CHAR = "*"


def mask_value(value: str, visible: int = _DEFAULT_VISIBLE) -> str:
    """Return a partially masked version of *value*.

    The last *visible* characters are kept in plain text; everything
    before them is replaced with ``*``.  If the value is shorter than
    or equal to *visible* the whole string is masked.
    """
    if len(value) <= visible:
        return _MASK_CHAR * len(value)
    hidden = len(value) - visible
    return _MASK_CHAR * hidden + value[-visible:]


@dataclass
class MaskedEntry:
    """An env entry whose value has been partially masked."""

    key: str
    original_value: str
    masked_value: str
    was_sensitive: bool

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MaskedEntry(key={self.key!r}, "
            f"masked_value={self.masked_value!r}, "
            f"was_sensitive={self.was_sensitive})"
        )


@dataclass
class MaskReport:
    """Collection of masked entries produced from a single file."""

    filename: str
    entries: List[MaskedEntry] = field(default_factory=list)

    @property
    def sensitive_count(self) -> int:
        return sum(1 for e in self.entries if e.was_sensitive)

    @property
    def plain_count(self) -> int:
        return len(self.entries) - self.sensitive_count


def mask_entries(
    entries: List[EnvEntry],
    filename: str = "",
    visible: int = _DEFAULT_VISIBLE,
) -> MaskReport:
    """Build a :class:`MaskReport` from *entries*.

    Sensitive keys are masked; non-sensitive keys keep their original
    value as both ``original_value`` and ``masked_value``.
    """
    report = MaskReport(filename=filename)
    for entry in entries:
        sensitive = is_sensitive(entry.key)
        masked = mask_value(entry.value, visible) if sensitive else entry.value
        report.entries.append(
            MaskedEntry(
                key=entry.key,
                original_value=entry.value,
                masked_value=masked,
                was_sensitive=sensitive,
            )
        )
    return report

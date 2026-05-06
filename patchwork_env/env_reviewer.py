"""env_reviewer.py – Summarises a set of EnvEntry objects into a human-readable
review report, highlighting quality signals gathered from other modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry
from patchwork_env.env_redactor import is_sensitive
from patchwork_env.env_placeholder import is_placeholder
from patchwork_env.env_classifier import classify_key


@dataclass
class ReviewFlag:
    key: str
    message: str
    severity: str  # "info" | "warning" | "error"

    def __repr__(self) -> str:  # pragma: no cover
        return f"ReviewFlag({self.key!r}, {self.severity}, {self.message!r})"


@dataclass
class ReviewReport:
    filename: str
    flags: List[ReviewFlag] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    @property
    def errors(self) -> List[ReviewFlag]:
        return [f for f in self.flags if f.severity == "error"]

    @property
    def warnings(self) -> List[ReviewFlag]:
        return [f for f in self.flags if f.severity == "warning"]

    @property
    def infos(self) -> List[ReviewFlag]:
        return [f for f in self.flags if f.severity == "info"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ReviewReport({self.filename!r}, flags={len(self.flags)}, "
            f"passed={self.passed})"
        )


def review_entries(entries: List[EnvEntry], filename: str = "<env>") -> ReviewReport:
    """Inspect *entries* and return a :class:`ReviewReport`."""
    report = ReviewReport(filename=filename)

    seen_keys: dict[str, int] = {}
    for entry in entries:
        if entry.key is None:
            continue

        key = entry.key

        # Duplicate key detection
        seen_keys[key] = seen_keys.get(key, 0) + 1
        if seen_keys[key] == 2:
            report.flags.append(
                ReviewFlag(key, f"Duplicate key '{key}' detected.", "error")
            )

        # Placeholder value
        if is_placeholder(entry.value or ""):
            report.flags.append(
                ReviewFlag(key, f"'{key}' appears to contain a placeholder value.", "warning")
            )

        # Sensitive key with empty value
        if is_sensitive(key) and not (entry.value or "").strip():
            report.flags.append(
                ReviewFlag(key, f"Sensitive key '{key}' has an empty value.", "error")
            )

        # Lowercase key
        if key != key.upper():
            report.flags.append(
                ReviewFlag(key, f"Key '{key}' is not uppercase.", "warning")
            )

        # Classification info
        category = classify_key(key)
        report.flags.append(
            ReviewFlag(key, f"Classified as '{category.value}'.", "info")
        )

    return report

"""Validation rules for .env file entries and diffs."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from patchwork_env.parser import EnvEntry


class Severity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: Severity

    def __repr__(self) -> str:
        return f"ValidationIssue({self.severity.value}: {self.key!r} — {self.message})"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == Severity.WARNING for i in self.issues)


_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')


def validate_entries(entries: List[EnvEntry]) -> ValidationResult:
    """Validate a list of parsed EnvEntry objects."""
    result = ValidationResult()
    seen_keys: dict[str, int] = {}

    for entry in entries:
        if entry.key is None:
            continue

        # Duplicate key check
        if entry.key in seen_keys:
            result.issues.append(ValidationIssue(
                key=entry.key,
                message=f"Duplicate key (first seen at line {seen_keys[entry.key]})",
                severity=Severity.ERROR,
            ))
        else:
            seen_keys[entry.key] = entry.lineno

        # Key naming convention
        if not _KEY_RE.match(entry.key):
            result.issues.append(ValidationIssue(
                key=entry.key,
                message="Key should be UPPER_SNAKE_CASE starting with a letter",
                severity=Severity.WARNING,
            ))

        # Empty value warning
        if entry.value == "":
            result.issues.append(ValidationIssue(
                key=entry.key,
                message="Key has an empty value",
                severity=Severity.WARNING,
            ))

    return result

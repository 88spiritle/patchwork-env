"""env_health.py – compute an overall health report for a .env file.

Combines lint, validation, placeholder, and duplicate checks into a
single HealthReport with a pass/fail status and a human-readable grade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class HealthReport:
    filename: str
    lint_error_count: int = 0
    lint_warning_count: int = 0
    validation_error_count: int = 0
    validation_warning_count: int = 0
    placeholder_count: int = 0
    duplicate_count: int = 0
    notes: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    @property
    def total_errors(self) -> int:
        return self.lint_error_count + self.validation_error_count

    @property
    def total_warnings(self) -> int:
        return self.lint_warning_count + self.validation_warning_count

    @property
    def is_healthy(self) -> bool:
        """Healthy means zero errors and no placeholders."""
        return self.total_errors == 0 and self.placeholder_count == 0

    @property
    def grade(self) -> str:
        if self.total_errors > 0:
            return "F"
        if self.placeholder_count > 0 or self.duplicate_count > 0:
            return "C"
        if self.total_warnings > 3:
            return "B"
        if self.total_warnings > 0:
            return "A-"
        return "A"

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"HealthReport(file={self.filename!r}, grade={self.grade!r}, "
            f"errors={self.total_errors}, warnings={self.total_warnings})"
        )


def build_health_report(
    filename: str,
    *,
    lint_errors: int = 0,
    lint_warnings: int = 0,
    validation_errors: int = 0,
    validation_warnings: int = 0,
    placeholders: int = 0,
    duplicates: int = 0,
    notes: List[str] | None = None,
) -> HealthReport:
    """Factory that assembles a HealthReport from pre-counted metrics."""
    return HealthReport(
        filename=filename,
        lint_error_count=lint_errors,
        lint_warning_count=lint_warnings,
        validation_error_count=validation_errors,
        validation_warning_count=validation_warnings,
        placeholder_count=placeholders,
        duplicate_count=duplicates,
        notes=notes or [],
    )

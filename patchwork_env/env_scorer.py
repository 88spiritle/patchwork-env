"""Score .env files for quality based on lint, redaction, and validation signals."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from patchwork_env.env_linter import LintResult, LintCode
from patchwork_env.validator import ValidationResult, Severity


@dataclass
class ScoreBreakdown:
    lint_penalty: int = 0
    validation_penalty: int = 0
    bonus: int = 0

    @property
    def total(self) -> int:
        base = 100 - self.lint_penalty - self.validation_penalty + self.bonus
        return max(0, min(100, base))


@dataclass
class EnvScore:
    filename: str
    breakdown: ScoreBreakdown
    notes: List[str] = field(default_factory=list)

    @property
    def grade(self) -> str:
        t = self.breakdown.total
        if t >= 90:
            return "A"
        if t >= 75:
            return "B"
        if t >= 60:
            return "C"
        if t >= 40:
            return "D"
        return "F"

    def __repr__(self) -> str:  # pragma: no cover
        return f"<EnvScore {self.filename!r} grade={self.grade} score={self.breakdown.total}>"


_LINT_PENALTY = {
    LintCode.MISSING_VALUE: 10,
    LintCode.DUPLICATE_KEY: 15,
    LintCode.INVALID_KEY_FORMAT: 8,
    LintCode.LOWERCASE_KEY: 3,
    LintCode.EMPTY_KEY: 12,
}


def score_env(filename: str, lint_result: LintResult, validation_result: ValidationResult) -> EnvScore:
    breakdown = ScoreBreakdown()
    notes: List[str] = []

    seen_codes: set = set()
    for issue in lint_result.issues:
        if issue.code not in seen_codes:
            penalty = _LINT_PENALTY.get(issue.code, 5)
            breakdown.lint_penalty = min(breakdown.lint_penalty + penalty, 60)
            seen_codes.add(issue.code)
            notes.append(f"Lint [{issue.code.value}]: {issue.message}")

    for issue in validation_result.issues:
        if issue.severity == Severity.ERROR:
            breakdown.validation_penalty = min(breakdown.validation_penalty + 10, 40)
            notes.append(f"Validation error: {issue.message}")
        elif issue.severity == Severity.WARNING:
            breakdown.validation_penalty = min(breakdown.validation_penalty + 3, 40)
            notes.append(f"Validation warning: {issue.message}")

    if not notes:
        breakdown.bonus = 5
        notes.append("No issues found — bonus applied.")

    return EnvScore(filename=filename, breakdown=breakdown, notes=notes)

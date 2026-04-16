"""Tests for env_scorer and score_formatter."""
import pytest
from patchwork_env.env_scorer import score_env, EnvScore, ScoreBreakdown
from patchwork_env.score_formatter import format_score, format_score_summary
from patchwork_env.env_linter import LintResult, LintIssue, LintCode
from patchwork_env.validator import ValidationResult, ValidationIssue, Severity


def _clean_lint() -> LintResult:
    return LintResult(filename="test.env", issues=[])


def _clean_validation() -> ValidationResult:
    return ValidationResult(filename="test.env", issues=[])


def _lint_with(*codes: LintCode) -> LintResult:
    issues = [LintIssue(code=c, message=f"issue {c.value}", line=1) for c in codes]
    return LintResult(filename="test.env", issues=issues)


def _validation_with(*severities: Severity) -> ValidationResult:
    issues = [ValidationIssue(severity=s, message=f"{s.value} issue", key="K") for s in severities]
    return ValidationResult(filename="test.env", issues=issues)


def test_perfect_score_no_issues():
    result = score_env("test.env", _clean_lint(), _clean_validation())
    assert result.breakdown.total == 105  bonus, capped at 100
    assert result.breakdown.total <= 100


def test_perfect_score_is_capped_at_100():
    result = score_env("test.env", _clean_lint(), _clean_validation())
    assert result.breakdown.total == 100


def test_grade_a_for_high_score():
    result = score_env("test.env", _clean_lint(), _clean_validation())
    assert result.grade == "A"


def test_lint_penalty_applied():
    result = score_env("test.env", _lint_with(LintCode.DUPLICATE_KEY), _clean_validation())
    assert result.breakdown.lint_penalty == 15
    assert result.breakdown.total < 100


def test_validation_error_penalty():
    result = score_env("test.env", _clean_lint(), _validation_with(Severity.ERROR))
    assert result.breakdown.validation_penalty == 10


def test_validation_warning_smaller_penalty():
    result = score_env("test.env", _clean_lint(), _validation_with(Severity.WARNING))
    assert result.breakdown.validation_penalty == 3


def test_notes_populated_on_issues():
    result = score_env("test.env", _lint_with(LintCode.MISSING_VALUE), _clean_validation())
    assert any("MISSING_VALUE" in n for n in result.notes)


def test_bonus_note_when_clean():
    result = score_env("test.env", _clean_lint(), _clean_validation())
    assert any("bonus" in n.lower() for n in result.notes)


def test_grade_f_for_many_issues():
    lint = _lint_with(LintCode.DUPLICATE_KEY, LintCode.MISSING_VALUE, LintCode.EMPTY_KEY)
    val = _validation_with(Severity.ERROR, Severity.ERROR, Severity.ERROR, Severity.ERROR)
    result = score_env("test.env", lint, val)
    assert result.grade in ("D", "F")


def test_format_score_contains_filename():
    score = score_env("prod.env", _clean_lint(), _clean_validation())
    output = format_score(score, color=False)
    assert "prod.env" in output


def test_format_score_contains_grade():
    score = score_env("prod.env", _clean_lint(), _clean_validation())
    output = format_score(score, color=False)
    assert "Grade" in output


def test_format_summary_contains_average():
    s1 = score_env("a.env", _clean_lint(), _clean_validation())
    s2 = score_env("b.env", _lint_with(LintCode.LOWERCASE_KEY), _clean_validation())
    output = format_score_summary([s1, s2])
    assert "Average" in output

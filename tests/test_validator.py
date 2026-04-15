"""Tests for patchwork_env.validator."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.validator import (
    Severity,
    ValidationIssue,
    ValidationResult,
    validate_entries,
)


def make_entry(key: str, value: str, lineno: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}", lineno=lineno)


# ---------------------------------------------------------------------------
# ValidationResult helpers
# ---------------------------------------------------------------------------

class TestValidationResult:
    def test_is_valid_no_issues(self):
        assert ValidationResult().is_valid is True

    def test_is_valid_only_warnings(self):
        r = ValidationResult(issues=[
            ValidationIssue("K", "warn", Severity.WARNING)
        ])
        assert r.is_valid is True

    def test_is_invalid_with_error(self):
        r = ValidationResult(issues=[
            ValidationIssue("K", "err", Severity.ERROR)
        ])
        assert r.is_valid is False

    def test_has_warnings(self):
        r = ValidationResult(issues=[
            ValidationIssue("K", "warn", Severity.WARNING)
        ])
        assert r.has_warnings is True


# ---------------------------------------------------------------------------
# validate_entries
# ---------------------------------------------------------------------------

def test_valid_entries_pass():
    entries = [
        make_entry("APP_ENV", "production", 1),
        make_entry("DB_HOST", "localhost", 2),
    ]
    result = validate_entries(entries)
    assert result.is_valid
    assert not result.has_warnings


def test_duplicate_key_is_error():
    entries = [
        make_entry("APP_ENV", "production", 1),
        make_entry("APP_ENV", "staging", 5),
    ]
    result = validate_entries(entries)
    assert not result.is_valid
    errors = [i for i in result.issues if i.severity == Severity.ERROR]
    assert len(errors) == 1
    assert "Duplicate" in errors[0].message


def test_lowercase_key_is_warning():
    entries = [make_entry("db_host", "localhost", 1)]
    result = validate_entries(entries)
    assert result.is_valid
    warnings = [i for i in result.issues if i.severity == Severity.WARNING]
    assert any("UPPER_SNAKE_CASE" in w.message for w in warnings)


def test_empty_value_is_warning():
    entries = [make_entry("SECRET_KEY", "", 1)]
    result = validate_entries(entries)
    assert result.is_valid
    warnings = [i for i in result.issues if i.severity == Severity.WARNING]
    assert any("empty" in w.message for w in warnings)


def test_comment_only_entries_are_skipped():
    comment = EnvEntry(key=None, value=None, raw="# just a comment", lineno=1)
    result = validate_entries([comment])
    assert result.is_valid
    assert result.issues == []


def test_validation_issue_repr():
    issue = ValidationIssue("MY_KEY", "something wrong", Severity.ERROR)
    assert "MY_KEY" in repr(issue)
    assert "error" in repr(issue)

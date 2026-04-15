"""Tests for patchwork_env.env_linter."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_linter import (
    LintCode,
    LintResult,
    lint_entries,
)


def _entry(key: str, value: str, lineno: int = 1, raw_value: str | None = None) -> EnvEntry:
    """Build a minimal EnvEntry for testing."""
    e = EnvEntry.__new__(EnvEntry)
    e.key = key
    e.value = value
    e.raw_value = raw_value if raw_value is not None else value
    e.lineno = lineno
    e.is_comment = False
    e.is_blank = False
    return e


def _blank() -> EnvEntry:
    e = EnvEntry.__new__(EnvEntry)
    e.key = ""
    e.value = ""
    e.raw_value = ""
    e.lineno = 0
    e.is_comment = False
    e.is_blank = True
    return e


# ---------------------------------------------------------------------------
# LintResult helpers
# ---------------------------------------------------------------------------

class TestLintResult:
    def test_passed_when_no_errors(self):
        r = LintResult(filename="f.env")
        assert r.passed is True

    def test_not_passed_when_error_present(self):
        r = LintResult(filename="f.env")
        r.issues.append(LintIssue_stub := object.__new__(type(
            "_", (), {"code": type("_", (), {"value": "E001"})()})))
        # Use real object instead
        from patchwork_env.env_linter import LintIssue
        r.issues.clear()
        r.issues.append(LintIssue(1, LintCode.UPPERCASE_KEY, "foo", "msg"))
        assert r.passed is False

    def test_errors_and_warnings_split(self):
        from patchwork_env.env_linter import LintIssue
        r = LintResult(filename="f.env")
        r.issues.append(LintIssue(1, LintCode.UPPERCASE_KEY, "foo", "e"))
        r.issues.append(LintIssue(2, LintCode.NO_VALUE, "FOO", "w"))
        assert len(r.errors) == 1
        assert len(r.warnings) == 1


# ---------------------------------------------------------------------------
# lint_entries rules
# ---------------------------------------------------------------------------

def test_clean_entry_produces_no_issues():
    entries = [_entry("DATABASE_URL", "postgres://localhost/db")]
    result = lint_entries(entries, "prod.env")
    assert result.passed
    assert result.issues == []


def test_lowercase_key_triggers_uppercase_rule():
    entries = [_entry("database_url", "postgres://localhost/db")]
    result = lint_entries(entries)
    codes = [i.code for i in result.issues]
    assert LintCode.UPPERCASE_KEY in codes


def test_empty_value_triggers_no_value_warning():
    entries = [_entry("API_KEY", "")]
    result = lint_entries(entries)
    codes = [i.code for i in result.issues]
    assert LintCode.NO_VALUE in codes


def test_key_with_space_triggers_whitespace_error():
    entries = [_entry("MY KEY", "val")]
    result = lint_entries(entries)
    codes = [i.code for i in result.issues]
    assert LintCode.WHITESPACE_IN_KEY in codes


def test_double_underscore_triggers_warning():
    entries = [_entry("MY__KEY", "val")]
    result = lint_entries(entries)
    codes = [i.code for i in result.issues]
    assert LintCode.DOUBLE_UNDERSCORE in codes


def test_very_long_value_triggers_warning():
    entries = [_entry("LONG_VAL", "x" * 257)]
    result = lint_entries(entries)
    codes = [i.code for i in result.issues]
    assert LintCode.VERY_LONG_VALUE in codes


def test_blank_lines_are_skipped():
    entries = [_blank(), _entry("GOOD_KEY", "value"), _blank()]
    result = lint_entries(entries)
    assert result.issues == []


def test_filename_stored_in_result():
    result = lint_entries([], filename="staging.env")
    assert result.filename == "staging.env"


def test_unquoted_leading_space_warning():
    entries = [_entry("MY_VAR", " value", raw_value=" value")]
    result = lint_entries(entries)
    codes = [i.code for i in result.issues]
    assert LintCode.LEADING_TRAILING_SPACE in codes


def test_quoted_value_skips_space_check():
    entries = [_entry("MY_VAR", " value", raw_value="' value'")]
    result = lint_entries(entries)
    codes = [i.code for i in result.issues]
    assert LintCode.LEADING_TRAILING_SPACE not in codes

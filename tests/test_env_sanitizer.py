"""Tests for patchwork_env.env_sanitizer and sanitize_formatter."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_sanitizer import (
    sanitize_entries,
    SanitizeResult,
    SanitizeIssue,
    _is_dangerous,
    _has_unmatched_quotes,
)
from patchwork_env.sanitize_formatter import format_sanitize_result, format_sanitize_summary


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


def _blank() -> EnvEntry:
    return EnvEntry(key=None, value="", raw="# comment")


# ---------------------------------------------------------------------------
# _is_dangerous
# ---------------------------------------------------------------------------

class TestIsDangerous:
    def test_command_substitution_dollar(self):
        assert _is_dangerous("$(whoami)")

    def test_backtick_substitution(self):
        assert _is_dangerous("`id`")

    def test_shell_and(self):
        assert _is_dangerous("foo && bar")

    def test_shell_or(self):
        assert _is_dangerous("foo || bar")

    def test_semicolon(self):
        assert _is_dangerous("foo; rm -rf /")

    def test_plain_value_is_safe(self):
        assert not _is_dangerous("plain_value_123")


# ---------------------------------------------------------------------------
# _has_unmatched_quotes
# ---------------------------------------------------------------------------

def test_unmatched_double_quote():
    assert _has_unmatched_quotes('hello"world')


def test_unmatched_single_quote():
    assert _has_unmatched_quotes("hello'world")


def test_matched_quotes_are_fine():
    assert not _has_unmatched_quotes('"hello"')


# ---------------------------------------------------------------------------
# sanitize_entries
# ---------------------------------------------------------------------------

class TestSanitizeEntries:
    def test_clean_entry_passes_through(self):
        entries = [_entry("HOST", "localhost")]
        result = sanitize_entries(entries, filename=".env")
        assert result.total_clean == 1
        assert result.total_issues == 0

    def test_dangerous_entry_is_flagged(self):
        entries = [_entry("CMD", "$(whoami)")]
        result = sanitize_entries(entries)
        assert result.total_issues == 1
        assert result.issues[0].key == "CMD"
        assert "dangerous" in result.issues[0].reason

    def test_unmatched_quote_is_flagged(self):
        entries = [_entry("VAL", 'hello"world')]
        result = sanitize_entries(entries)
        assert result.total_issues == 1
        assert "quote" in result.issues[0].reason

    def test_blank_line_passes_through(self):
        entries = [_blank()]
        result = sanitize_entries(entries)
        assert result.total_clean == 1
        assert result.total_issues == 0

    def test_filename_stored(self):
        result = sanitize_entries([], filename="staging.env")
        assert result.filename == "staging.env"

    def test_has_issues_false_when_clean(self):
        result = sanitize_entries([_entry("A", "ok")])
        assert not result.has_issues

    def test_has_issues_true_when_flagged(self):
        result = sanitize_entries([_entry("X", "$(bad)")])
        assert result.has_issues


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------

def test_format_result_contains_filename():
    result = sanitize_entries([_entry("A", "clean")], filename="prod.env")
    output = format_sanitize_result(result)
    assert "prod.env" in output


def test_format_result_shows_clean_message():
    result = sanitize_entries([_entry("A", "clean")])
    output = format_sanitize_result(result)
    assert "clean" in output.lower()


def test_format_result_shows_issue_key():
    result = sanitize_entries([_entry("DANGER", "$(rm -rf /)")])
    output = format_sanitize_result(result)
    assert "DANGER" in output


def test_format_summary_shows_file_count():
    r1 = sanitize_entries([_entry("A", "ok")], filename="a.env")
    r2 = sanitize_entries([_entry("B", "$(bad)")], filename="b.env")
    output = format_sanitize_summary([r1, r2])
    assert "2" in output

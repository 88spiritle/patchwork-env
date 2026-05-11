"""Tests for env_truncator and truncate_formatter."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_truncator import (
    TruncateRecord,
    TruncateResult,
    truncate_entries,
    DEFAULT_MAX_LENGTH,
)
from patchwork_env.truncate_formatter import (
    format_truncate_result,
    format_truncate_summary,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# TruncateRecord
# ---------------------------------------------------------------------------

class TestTruncateRecord:
    def test_was_truncated_flag_true(self):
        rec = TruncateRecord("KEY", "abc" * 40, "abc", True)
        assert rec.was_truncated is True

    def test_was_truncated_flag_false(self):
        rec = TruncateRecord("KEY", "short", "short", False)
        assert rec.was_truncated is False


# ---------------------------------------------------------------------------
# TruncateResult
# ---------------------------------------------------------------------------

class TestTruncateResult:
    def test_was_clean_when_no_truncations(self):
        res = TruncateResult(filename=".env")
        res.records.append(TruncateRecord("A", "x", "x", False))
        assert res.was_clean is True

    def test_not_clean_when_truncated(self):
        res = TruncateResult(filename=".env")
        res.records.append(TruncateRecord("A", "x" * 100, "x" * 80, True))
        assert res.was_clean is False

    def test_total_truncated_counts_only_truncated(self):
        res = TruncateResult(filename=".env")
        res.records.append(TruncateRecord("A", "x" * 100, "x" * 80, True))
        res.records.append(TruncateRecord("B", "short", "short", False))
        assert res.total_truncated == 1


# ---------------------------------------------------------------------------
# truncate_entries
# ---------------------------------------------------------------------------

def test_short_value_not_truncated():
    entries = [_entry("KEY", "hello")]
    result = truncate_entries(entries, filename=".env", max_length=20)
    assert result.records[0].was_truncated is False
    assert result.records[0].truncated_value == "hello"


def test_long_value_is_truncated():
    long_val = "x" * 120
    entries = [_entry("KEY", long_val)]
    result = truncate_entries(entries, filename=".env", max_length=80)
    rec = result.records[0]
    assert rec.was_truncated is True
    assert len(rec.truncated_value) == 80
    assert rec.original_value == long_val


def test_exact_length_not_truncated():
    val = "a" * DEFAULT_MAX_LENGTH
    entries = [_entry("KEY", val)]
    result = truncate_entries(entries)
    assert result.records[0].was_truncated is False


def test_filename_stored_in_result():
    result = truncate_entries([], filename="prod.env")
    assert result.filename == "prod.env"


def test_empty_entries_returns_clean_result():
    result = truncate_entries([], filename=".env")
    assert result.was_clean is True
    assert result.total_truncated == 0


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_result_contains_filename():
    result = truncate_entries([_entry("FOO", "bar")], filename="staging.env")
    output = format_truncate_result(result)
    assert "staging.env" in output


def test_format_result_shows_truncated_key():
    entries = [_entry("LONG_KEY", "v" * 200)]
    result = truncate_entries(entries, filename=".env", max_length=50)
    output = format_truncate_result(result, max_length=50)
    assert "LONG_KEY" in output
    assert "TRUNCATED" in output


def test_format_result_shows_clean_message_when_no_truncations():
    result = truncate_entries([_entry("A", "short")], filename=".env")
    output = format_truncate_result(result)
    assert "No values exceeded" in output


def test_format_summary_clean():
    result = truncate_entries([_entry("A", "ok")], filename="dev.env")
    summary = format_truncate_summary(result)
    assert "dev.env" in summary
    assert "clean" in summary


def test_format_summary_shows_truncated_count():
    entries = [_entry("X", "z" * 200)]
    result = truncate_entries(entries, filename="prod.env", max_length=10)
    summary = format_truncate_summary(result)
    assert "1 truncated" in summary

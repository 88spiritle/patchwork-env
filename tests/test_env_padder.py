"""Tests for env_padder module."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_padder import PaddedLine, PadResult, pad_entries
from patchwork_env.pad_formatter import format_pad_result, format_pad_summary


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# pad_entries
# ---------------------------------------------------------------------------

def test_empty_entries_returns_empty_result():
    result = pad_entries([], filename="test.env")
    assert result.total_entries == 0
    assert result.width == 0


def test_width_equals_longest_key():
    entries = [_entry("DB", "localhost"), _entry("DATABASE_HOST", "127.0.0.1")]
    result = pad_entries(entries, filename="test.env")
    assert result.width == len("DATABASE_HOST")


def test_padded_text_keys_are_equal_length():
    entries = [_entry("A", "1"), _entry("LONG_KEY", "2"), _entry("MED", "3")]
    result = pad_entries(entries)
    widths = [line.padded_text.index(" ") for line in result.lines]
    assert len(set(widths)) == 1


def test_padded_text_contains_value():
    entries = [_entry("KEY", "secret"), _entry("LONG_KEY", "other")]
    result = pad_entries(entries)
    assert "secret" in result.lines[0].padded_text
    assert "other" in result.lines[1].padded_text


def test_padded_text_format_uses_equals_separator():
    entries = [_entry("KEY", "val")]
    result = pad_entries(entries)
    assert "=" in result.lines[0].padded_text


def test_filename_stored():
    result = pad_entries([_entry("X", "1")], filename="prod.env")
    assert result.filename == "prod.env"


# ---------------------------------------------------------------------------
# PadResult.was_already_aligned
# ---------------------------------------------------------------------------

def test_was_already_aligned_uniform_keys():
    entries = [_entry("KEY", "a"), _entry("FOO", "b"), _entry("BAR", "c")]
    result = pad_entries(entries)
    assert result.was_already_aligned is True


def test_was_not_aligned_mixed_key_lengths():
    entries = [_entry("A", "1"), _entry("LONG_KEY", "2")]
    result = pad_entries(entries)
    # After padding, was_already_aligned checks if all originals match width
    assert result.was_already_aligned is False


def test_empty_result_is_considered_aligned():
    result = pad_entries([])
    assert result.was_already_aligned is True


# ---------------------------------------------------------------------------
# Formatter smoke tests
# ---------------------------------------------------------------------------

def test_format_pad_result_contains_filename():
    entries = [_entry("DB_HOST", "localhost")]
    result = pad_entries(entries, filename="staging.env")
    output = format_pad_result(result)
    assert "staging.env" in output


def test_format_pad_result_contains_all_keys():
    entries = [_entry("DB_HOST", "localhost"), _entry("PORT", "5432")]
    result = pad_entries(entries, filename="dev.env")
    output = format_pad_result(result)
    assert "DB_HOST" in output
    assert "PORT" in output


def test_format_pad_summary_contains_filename():
    entries = [_entry("KEY", "val")]
    result = pad_entries(entries, filename="base.env")
    summary = format_pad_summary(result)
    assert "base.env" in summary


def test_format_pad_summary_contains_entry_count():
    entries = [_entry("A", "1"), _entry("B", "2")]
    result = pad_entries(entries, filename="x.env")
    summary = format_pad_summary(result)
    assert "2" in summary

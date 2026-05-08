"""Tests for env_summarizer and summarizer_formatter."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_summarizer import summarize, EnvSummary
from patchwork_env.summarizer_formatter import format_summary, format_summary_oneliner


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# summarize()
# ---------------------------------------------------------------------------

def test_empty_entries_returns_zero_totals():
    s = summarize([], filename="empty.env")
    assert s.total_keys == 0
    assert s.empty_values == 0
    assert s.commented_lines == 0
    assert s.unique_prefixes == []


def test_total_keys_counted():
    entries = [_entry("DB_HOST"), _entry("DB_PORT"), _entry("APP_NAME")]
    s = summarize(entries, filename="test.env")
    assert s.total_keys == 3


def test_empty_values_counted():
    entries = [_entry("FOO", ""), _entry("BAR", ""), _entry("BAZ", "set")]
    s = summarize(entries, filename="test.env")
    assert s.empty_values == 2


def test_unique_prefixes_extracted():
    entries = [
        _entry("DB_HOST"),
        _entry("DB_PORT"),
        _entry("APP_NAME"),
        _entry("APP_ENV"),
        _entry("SECRET"),
    ]
    s = summarize(entries)
    assert set(s.unique_prefixes) == {"DB", "APP", "SECRET"}


def test_unique_prefixes_sorted():
    entries = [_entry("Z_KEY"), _entry("A_KEY"), _entry("M_KEY")]
    s = summarize(entries)
    assert s.unique_prefixes == sorted(s.unique_prefixes)


def test_longest_key_identified():
    entries = [_entry("SHORT"), _entry("MUCH_LONGER_KEY_NAME"), _entry("MID")]
    s = summarize(entries)
    assert s.longest_key == "MUCH_LONGER_KEY_NAME"


def test_longest_value_key_identified():
    entries = [
        _entry("A", "short"),
        _entry("B", "a_very_long_value_indeed"),
        _entry("C", "mid"),
    ]
    s = summarize(entries)
    assert s.longest_value_key == "B"


def test_filename_stored():
    s = summarize([_entry("X")], filename="prod.env")
    assert s.filename == "prod.env"


# ---------------------------------------------------------------------------
# format_summary()
# ---------------------------------------------------------------------------

def test_format_summary_contains_filename():
    s = summarize([_entry("DB_HOST")], filename="staging.env")
    output = format_summary(s)
    assert "staging.env" in output


def test_format_summary_shows_total_keys():
    entries = [_entry(f"KEY_{i}") for i in range(5)]
    s = summarize(entries, filename="x.env")
    output = format_summary(s)
    assert "5" in output


def test_format_summary_shows_prefixes():
    entries = [_entry("DB_HOST"), _entry("APP_NAME")]
    s = summarize(entries, filename="x.env")
    output = format_summary(s)
    assert "DB" in output
    assert "APP" in output


def test_format_summary_oneliner_contains_filename():
    s = summarize([_entry("X")], filename="dev.env")
    line = format_summary_oneliner(s)
    assert "dev.env" in line


def test_format_summary_oneliner_contains_key_count():
    entries = [_entry(f"K{i}") for i in range(3)]
    s = summarize(entries, filename="dev.env")
    line = format_summary_oneliner(s)
    assert "3" in line

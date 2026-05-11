"""Tests for env_highlighter and highlight_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.env_highlighter import (
    HighlightRecord,
    HighlightResult,
    highlight_entries,
)
from patchwork_env.highlight_formatter import (
    format_highlight_result,
    format_highlight_summary,
)
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str = "val") -> EnvEntry:
    e = EnvEntry.__new__(EnvEntry)
    e.key = key
    e.value = value
    e.comment = None
    e.raw = f"{key}={value}"
    return e


@pytest.fixture()
def entries() -> list[EnvEntry]:
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("SECRET_KEY", "abc123"),
        _entry("DEBUG", "true"),
    ]


# --- highlight_entries ---

def test_highlight_returns_result(entries):
    result = highlight_entries(entries, ["DB_HOST"], filename=".env")
    assert isinstance(result, HighlightResult)


def test_highlight_matched_key_found(entries):
    result = highlight_entries(entries, ["DB_HOST"], filename=".env")
    assert "DB_HOST" in result.highlighted_keys


def test_highlight_unmatched_key_excluded(entries):
    result = highlight_entries(entries, ["DB_HOST"], filename=".env")
    assert "DEBUG" not in result.highlighted_keys


def test_highlight_case_insensitive(entries):
    result = highlight_entries(entries, ["secret_key"], filename=".env")
    assert "SECRET_KEY" in result.highlighted_keys


def test_highlight_multiple_keys(entries):
    result = highlight_entries(entries, ["DB_HOST", "DB_PORT"], filename=".env")
    assert result.total_highlighted == 2


def test_highlight_no_match_returns_empty(entries):
    result = highlight_entries(entries, ["NONEXISTENT"], filename=".env")
    assert result.total_highlighted == 0
    assert result.highlighted == []


def test_highlight_total_entries_set(entries):
    result = highlight_entries(entries, ["DB_HOST"], filename=".env")
    assert result.total_entries == len(entries)


def test_highlight_reason_stored(entries):
    result = highlight_entries(entries, ["DEBUG"], filename=".env", reason="review")
    assert result.highlighted[0].reason == "review"


def test_highlight_reason_none_by_default(entries):
    result = highlight_entries(entries, ["DEBUG"], filename=".env")
    assert result.highlighted[0].reason is None


def test_highlight_filename_stored(entries):
    result = highlight_entries(entries, ["DEBUG"], filename="prod.env")
    assert result.filename == "prod.env"


# --- format_highlight_result ---

def test_format_result_contains_filename(entries):
    result = highlight_entries(entries, ["DB_HOST"], filename=".env")
    text = format_highlight_result(result)
    assert ".env" in text


def test_format_result_shows_highlighted_key(entries):
    result = highlight_entries(entries, ["DB_HOST"], filename=".env")
    text = format_highlight_result(result)
    assert "DB_HOST" in text


def test_format_result_clean_message_when_no_match(entries):
    result = highlight_entries(entries, ["MISSING"], filename=".env")
    text = format_highlight_result(result)
    assert "No keys matched" in text


# --- format_highlight_summary ---

def test_summary_contains_filename(entries):
    result = highlight_entries(entries, ["DB_HOST"], filename=".env")
    text = format_highlight_summary(result)
    assert ".env" in text


def test_summary_shows_highlighted_status(entries):
    result = highlight_entries(entries, ["DB_HOST"], filename=".env")
    text = format_highlight_summary(result)
    assert "HIGHLIGHTED" in text


def test_summary_shows_clean_when_no_match(entries):
    result = highlight_entries(entries, ["MISSING"], filename=".env")
    text = format_highlight_summary(result)
    assert "CLEAN" in text

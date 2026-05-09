"""Tests for patchwork_env.selector_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_selector import SelectionCriteria, SelectionResult, select_entries
from patchwork_env.selector_formatter import (
    format_selection_result,
    format_selection_summary,
)


def _entry(key: str, value: str = "val") -> EnvEntry:
    e = EnvEntry.__new__(EnvEntry)
    e.key = key
    e.value = value
    e.raw_line = f"{key}={value}"
    e.comment = None
    return e


@pytest.fixture()
def sample_result() -> SelectionResult:
    entries = [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("APP_SECRET", "abc123"),
    ]
    return select_entries(
        entries, SelectionCriteria(prefix="DB_"), filename="prod.env"
    )


def test_format_result_contains_filename(sample_result):
    out = format_selection_result(sample_result)
    assert "prod.env" in out


def test_format_result_shows_selected_count(sample_result):
    out = format_selection_result(sample_result)
    assert "2" in out


def test_format_result_shows_excluded_count(sample_result):
    out = format_selection_result(sample_result)
    assert "1" in out


def test_format_result_shows_matched_keys(sample_result):
    out = format_selection_result(sample_result)
    assert "DB_HOST" in out
    assert "DB_PORT" in out


def test_format_result_does_not_show_excluded_key(sample_result):
    out = format_selection_result(sample_result)
    assert "APP_SECRET" not in out


def test_format_result_empty_match():
    entries = [_entry("FOO", "bar")]
    result = select_entries(
        entries, SelectionCriteria(prefix="DB_"), filename="dev.env"
    )
    out = format_selection_result(result)
    assert "no entries matched" in out


def test_summary_contains_filename(sample_result):
    out = format_selection_summary(sample_result)
    assert "prod.env" in out


def test_summary_shows_ratio(sample_result):
    out = format_selection_summary(sample_result)
    assert "2/3" in out


def test_summary_ok_when_selected(sample_result):
    out = format_selection_summary(sample_result)
    assert "OK" in out


def test_summary_empty_when_none_selected():
    entries = [_entry("FOO", "bar")]
    result = select_entries(
        entries, SelectionCriteria(prefix="ZZ_"), filename="dev.env"
    )
    out = format_selection_summary(result)
    assert "EMPTY" in out

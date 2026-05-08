"""Tests for patchwork_env.filter_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_filter import FilterCriteria, FilterResult, filter_entries
from patchwork_env.filter_formatter import format_filter_result, format_filter_summary


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}", comment=None)


@pytest.fixture()
def sample_result() -> FilterResult:
    entries = [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("APP_SECRET", "s3cr3t"),
    ]
    return filter_entries(
        entries,
        FilterCriteria(key_pattern="^DB_"),
        filename="staging.env",
    )


def test_format_result_contains_filename(sample_result):
    output = format_filter_result(sample_result)
    assert "staging.env" in output


def test_format_result_shows_matched_keys(sample_result):
    output = format_filter_result(sample_result)
    assert "DB_HOST" in output
    assert "DB_PORT" in output


def test_format_result_excludes_non_matched(sample_result):
    output = format_filter_result(sample_result)
    assert "APP_SECRET" not in output


def test_format_result_shows_key_pattern(sample_result):
    output = format_filter_result(sample_result)
    assert "^DB_" in output


def test_format_result_empty_match_shows_message():
    result = filter_entries(
        [_entry("FOO", "bar")],
        FilterCriteria(key_pattern="^NOMATCH"),
        filename="test.env",
    )
    output = format_filter_result(result)
    assert "no entries matched" in output


def test_format_summary_contains_filename(sample_result):
    summary = format_filter_summary(sample_result)
    assert "staging.env" in summary


def test_format_summary_shows_matched_count(sample_result):
    summary = format_filter_summary(sample_result)
    assert "2 matched" in summary


def test_format_summary_shows_excluded_count(sample_result):
    summary = format_filter_summary(sample_result)
    assert "1 excluded" in summary


def test_format_summary_shows_total(sample_result):
    summary = format_filter_summary(sample_result)
    assert "3 total" in summary


def test_format_summary_zero_matches_shows_dash():
    result = filter_entries(
        [_entry("FOO", "bar")],
        FilterCriteria(key_pattern="^NOMATCH"),
        filename="test.env",
    )
    summary = format_filter_summary(result)
    assert "0 matched" in summary

"""Tests for patchwork_env.env_filter."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_filter import FilterCriteria, FilterResult, filter_entries


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}", comment=None)


@pytest.fixture()
def entries() -> list[EnvEntry]:
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("APP_SECRET", "s3cr3t"),
        _entry("APP_DEBUG", ""),
        _entry("LOG_LEVEL", "info"),
    ]


def test_no_criteria_returns_all(entries):
    result = filter_entries(entries, FilterCriteria(), filename="test.env")
    assert result.total_matched == len(entries)


def test_key_pattern_filters_by_prefix(entries):
    result = filter_entries(entries, FilterCriteria(key_pattern="^DB_"), filename="test.env")
    assert result.total_matched == 2
    keys = {e.key for e in result.matched}
    assert keys == {"DB_HOST", "DB_PORT"}


def test_key_pattern_is_case_insensitive(entries):
    result = filter_entries(entries, FilterCriteria(key_pattern="db_"), filename="test.env")
    assert result.total_matched == 2


def test_value_pattern_filters_by_value(entries):
    result = filter_entries(entries, FilterCriteria(value_pattern="^5"), filename="test.env")
    assert result.total_matched == 1
    assert result.matched[0].key == "DB_PORT"


def test_exclude_empty_removes_blank_values(entries):
    result = filter_entries(entries, FilterCriteria(exclude_empty=True), filename="test.env")
    assert all((e.value or "").strip() for e in result.matched)
    assert result.total_matched == 4


def test_invert_returns_non_matching(entries):
    result = filter_entries(
        entries, FilterCriteria(key_pattern="^DB_", invert=True), filename="test.env"
    )
    assert result.total_matched == 3
    assert all(not e.key.startswith("DB_") for e in result.matched)


def test_total_input_is_set(entries):
    result = filter_entries(entries, FilterCriteria(), filename="test.env")
    assert result.total_input == len(entries)


def test_total_excluded_is_correct(entries):
    result = filter_entries(entries, FilterCriteria(key_pattern="^DB_"), filename="test.env")
    assert result.total_excluded == result.total_input - result.total_matched


def test_filename_is_stored(entries):
    result = filter_entries(entries, FilterCriteria(), filename="prod.env")
    assert result.filename == "prod.env"


def test_combined_key_and_value_pattern(entries):
    result = filter_entries(
        entries,
        FilterCriteria(key_pattern="^APP_", value_pattern="s3cr"),
        filename="test.env",
    )
    assert result.total_matched == 1
    assert result.matched[0].key == "APP_SECRET"


def test_empty_entries_list():
    result = filter_entries([], FilterCriteria(key_pattern="DB"), filename="empty.env")
    assert result.total_matched == 0
    assert result.total_input == 0

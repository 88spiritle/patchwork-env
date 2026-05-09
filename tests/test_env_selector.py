"""Tests for patchwork_env.env_selector."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_selector import (
    SelectionCriteria,
    SelectionResult,
    select_entries,
)


def _entry(key: str, value: str = "val") -> EnvEntry:
    e = EnvEntry.__new__(EnvEntry)
    e.key = key
    e.value = value
    e.raw_line = f"{key}={value}"
    e.comment = None
    return e


@pytest.fixture()
def entries() -> list[EnvEntry]:
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("APP_SECRET", "abc123"),
        _entry("APP_DEBUG", ""),
        _entry("REDIS_URL", "redis://localhost"),
    ]


def test_no_criteria_selects_all(entries):
    result = select_entries(entries, SelectionCriteria(), filename="test.env")
    assert result.total_selected == len(entries)
    assert result.total_excluded == 0


def test_key_filter_exact_match(entries):
    result = select_entries(
        entries, SelectionCriteria(keys=["DB_HOST"]), filename="test.env"
    )
    assert result.total_selected == 1
    assert result.selected[0].key == "DB_HOST"


def test_key_filter_case_insensitive(entries):
    result = select_entries(
        entries, SelectionCriteria(keys=["db_host"]), filename="test.env"
    )
    assert result.total_selected == 1


def test_prefix_filter(entries):
    result = select_entries(
        entries, SelectionCriteria(prefix="DB_"), filename="test.env"
    )
    assert result.total_selected == 2
    keys = {e.key for e in result.selected}
    assert keys == {"DB_HOST", "DB_PORT"}


def test_suffix_filter(entries):
    result = select_entries(
        entries, SelectionCriteria(suffix="_URL"), filename="test.env"
    )
    assert result.total_selected == 1
    assert result.selected[0].key == "REDIS_URL"


def test_has_value_true(entries):
    result = select_entries(
        entries, SelectionCriteria(has_value=True), filename="test.env"
    )
    # APP_DEBUG has empty value
    assert result.total_selected == 4


def test_has_value_false(entries):
    result = select_entries(
        entries, SelectionCriteria(has_value=False), filename="test.env"
    )
    assert result.total_selected == 1
    assert result.selected[0].key == "APP_DEBUG"


def test_value_contains_filter(entries):
    result = select_entries(
        entries, SelectionCriteria(value_contains="localhost"), filename="test.env"
    )
    assert result.total_selected == 2


def test_combined_prefix_and_has_value(entries):
    result = select_entries(
        entries,
        SelectionCriteria(prefix="APP_", has_value=True),
        filename="test.env",
    )
    assert result.total_selected == 1
    assert result.selected[0].key == "APP_SECRET"


def test_filename_stored(entries):
    result = select_entries(entries, SelectionCriteria(), filename="my.env")
    assert result.filename == "my.env"


def test_excluded_count(entries):
    result = select_entries(
        entries, SelectionCriteria(prefix="DB_"), filename="test.env"
    )
    assert result.total_excluded == 3

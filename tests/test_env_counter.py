"""Tests for patchwork_env.env_counter."""
from __future__ import annotations

import pytest

from patchwork_env.env_counter import CountBreakdown, _extract_prefix, count_entries
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str = "val", comment: str = "") -> EnvEntry:
    return EnvEntry(key=key, value=value, inline_comment=comment, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# _extract_prefix
# ---------------------------------------------------------------------------

def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_underscore():
    assert _extract_prefix("PORT") == "PORT"


def test_extract_prefix_lowercased_input_normalised():
    assert _extract_prefix("aws_region") == "AWS"


# ---------------------------------------------------------------------------
# count_entries
# ---------------------------------------------------------------------------

@pytest.fixture()
def entries():
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("AWS_KEY", "abc123"),
        _entry("DEBUG", ""),          # empty value
        _entry("SECRET", ""),         # empty value
    ]


def test_total_counts_all_entries(entries):
    result = count_entries(entries, filename=".env")
    assert result.total == 5


def test_with_values_counts_non_empty(entries):
    result = count_entries(entries)
    assert result.with_values == 3


def test_empty_values_counts_blank(entries):
    result = count_entries(entries)
    assert result.empty_values == 2


def test_unique_prefixes_detected(entries):
    # DB, AWS, DEBUG, SECRET  -> 4 unique prefixes
    result = count_entries(entries)
    assert result.unique_prefixes == 4


def test_prefixes_list_sorted(entries):
    result = count_entries(entries)
    assert result._prefixes == sorted(result._prefixes)


def test_commented_out_passthrough():
    result = count_entries([], commented_lines=7)
    assert result.commented_out == 7


def test_filename_stored():
    result = count_entries([], filename="production.env")
    assert result.filename == "production.env"


def test_empty_entries_all_zeros():
    result = count_entries([])
    assert result.total == 0
    assert result.with_values == 0
    assert result.empty_values == 0
    assert result.unique_prefixes == 0


def test_single_entry_with_value():
    result = count_entries([_entry("PORT", "8080")])
    assert result.total == 1
    assert result.with_values == 1
    assert result.empty_values == 0


def test_returns_count_breakdown_instance():
    result = count_entries([])
    assert isinstance(result, CountBreakdown)

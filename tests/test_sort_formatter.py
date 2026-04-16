"""Tests for patchwork_env.sort_formatter."""

from __future__ import annotations

from patchwork_env.parser import EnvEntry
from patchwork_env.sort_formatter import format_grouped_entries, format_sorted_entries


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw_line=f"{key}={value}")


_ENTRIES = [
    _entry("APP_HOST", "localhost"),
    _entry("DB_PORT", "5432"),
    _entry("ZEBRA", "yes"),
]

_GROUPS = {
    "APP": [_entry("APP_HOST", "localhost"), _entry("APP_PORT", "8080")],
    "DB": [_entry("DB_HOST", "db"), _entry("DB_PORT", "5432")],
}


def test_format_sorted_entries_contains_header():
    out = format_sorted_entries(_ENTRIES)
    assert "Sorted entries" in out


def test_format_sorted_entries_shows_all_keys():
    out = format_sorted_entries(_ENTRIES)
    for entry in _ENTRIES:
        assert entry.key in out


def test_format_sorted_entries_shows_values():
    out = format_sorted_entries(_ENTRIES)
    assert "localhost" in out
    assert "5432" in out


def test_format_sorted_entries_includes_filename():
    out = format_sorted_entries(_ENTRIES, filename="prod.env")
    assert "prod.env" in out


def test_format_sorted_entries_shows_count():
    out = format_sorted_entries(_ENTRIES)
    assert "3" in out


def test_format_grouped_entries_contains_header():
    out = format_grouped_entries(_GROUPS)
    assert "Grouped entries" in out


def test_format_grouped_entries_shows_prefixes():
    out = format_grouped_entries(_GROUPS)
    assert "APP" in out
    assert "DB" in out


def test_format_grouped_entries_shows_all_keys():
    out = format_grouped_entries(_GROUPS)
    for members in _GROUPS.values():
        for entry in members:
            assert entry.key in out


def test_format_grouped_entries_includes_filename():
    out = format_grouped_entries(_GROUPS, filename="staging.env")
    assert "staging.env" in out


def test_format_grouped_entries_shows_group_count():
    out = format_grouped_entries(_GROUPS)
    assert "2 group" in out

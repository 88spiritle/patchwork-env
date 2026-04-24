"""Tests for patchwork_env.env_splitter."""

from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_splitter import split_by_prefixes, EnvSection, SplitResult


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


@pytest.fixture()
def entries() -> list[EnvEntry]:
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("AWS_ACCESS_KEY", "AKIA123"),
        _entry("AWS_SECRET", "secret"),
        _entry("APP_DEBUG", "true"),
        _entry("UNRELATED", "stuff"),
    ]


def test_split_creates_sections_for_matched_prefixes(entries):
    result = split_by_prefixes(entries, ["DB_", "AWS_"], filename=".env")
    assert "DB_" in [s.prefix for s in result.sections]
    assert "AWS_" in [s.prefix for s in result.sections]


def test_split_section_contains_correct_entries(entries):
    result = split_by_prefixes(entries, ["DB_"], filename=".env")
    db_section = next(s for s in result.sections if s.prefix == "DB_")
    assert len(db_section.entries) == 2
    assert all(e.key.startswith("DB_") for e in db_section.entries)


def test_unmatched_entries_go_to_uncategorised(entries):
    result = split_by_prefixes(entries, ["DB_", "AWS_"], filename=".env")
    uncategorised_keys = [e.key for e in result.uncategorised]
    assert "APP_DEBUG" in uncategorised_keys
    assert "UNRELATED" in uncategorised_keys


def test_total_entries_accounts_for_all(entries):
    result = split_by_prefixes(entries, ["DB_", "AWS_"], filename=".env")
    assert result.total_entries == len(entries)


def test_section_names_derived_from_prefix(entries):
    result = split_by_prefixes(entries, ["DB_", "AWS_"], filename=".env")
    assert "DB" in result.section_names
    assert "AWS" in result.section_names


def test_longest_prefix_wins_on_overlap():
    e = _entry("DB_REPLICA_HOST", "replica")
    result = split_by_prefixes([e], ["DB_", "DB_REPLICA_"], filename=".env")
    replica_section = next((s for s in result.sections if s.prefix == "DB_REPLICA_"), None)
    assert replica_section is not None
    assert len(replica_section.entries) == 1
    db_section = next((s for s in result.sections if s.prefix == "DB_"), None)
    assert db_section is None


def test_empty_entries_returns_empty_result():
    result = split_by_prefixes([], ["DB_"], filename=".env")
    assert result.sections == []
    assert result.uncategorised == []
    assert result.total_entries == 0


def test_no_prefixes_all_uncategorised(entries):
    result = split_by_prefixes(entries, [], filename=".env")
    assert len(result.uncategorised) == len(entries)
    assert result.sections == []


def test_filename_stored(entries):
    result = split_by_prefixes(entries, ["DB_"], filename="production.env")
    assert result.filename == "production.env"


def test_section_names_property(entries):
    result = split_by_prefixes(entries, ["DB_", "AWS_"], filename=".env")
    names = result.section_names
    assert isinstance(names, list)
    assert len(names) == 2

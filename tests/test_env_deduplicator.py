"""Tests for patchwork_env.env_deduplicator."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_deduplicator import (
    KeepPolicy,
    DeduplicateRecord,
    DeduplicateResult,
    deduplicate,
)


def _entry(key: str, value: str, line: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}", line_number=line)


@pytest.fixture()
def entries_with_dupes():
    return [
        _entry("HOST", "localhost", 1),
        _entry("PORT", "5432", 2),
        _entry("HOST", "prod.example.com", 3),
        _entry("DB", "mydb", 4),
        _entry("HOST", "staging.example.com", 5),
    ]


def test_no_duplicates_returns_clean_result():
    entries = [_entry("A", "1", 1), _entry("B", "2", 2)]
    result = deduplicate(entries, filename="test.env")
    assert result.total_removed == 0
    assert result.affected_keys == []
    assert len(result.clean_entries) == 2


def test_keeps_last_by_default(entries_with_dupes):
    result = deduplicate(entries_with_dupes, filename="test.env")
    host_entry = next(e for e in result.clean_entries if e.key == "HOST")
    assert host_entry.value == "staging.example.com"
    assert host_entry.line_number == 5


def test_keeps_first_with_policy(entries_with_dupes):
    result = deduplicate(entries_with_dupes, filename="test.env", policy=KeepPolicy.FIRST)
    host_entry = next(e for e in result.clean_entries if e.key == "HOST")
    assert host_entry.value == "localhost"
    assert host_entry.line_number == 1


def test_total_removed_counts_all_discards(entries_with_dupes):
    result = deduplicate(entries_with_dupes, filename="test.env")
    assert result.total_removed == 2


def test_affected_keys_lists_duplicated_keys(entries_with_dupes):
    result = deduplicate(entries_with_dupes, filename="test.env")
    assert "HOST" in result.affected_keys
    assert "PORT" not in result.affected_keys


def test_clean_entries_preserves_order(entries_with_dupes):
    result = deduplicate(entries_with_dupes, filename="test.env")
    keys = [e.key for e in result.clean_entries]
    # HOST should still appear, PORT and DB should be in original relative order
    assert keys.index("PORT") < keys.index("DB")


def test_non_key_entries_are_preserved():
    blank = EnvEntry(key=None, value=None, raw="", line_number=1)
    entries = [blank, _entry("X", "1", 2)]
    result = deduplicate(entries)
    assert blank in result.clean_entries


def test_filename_stored():
    result = deduplicate([], filename="my.env")
    assert result.filename == "my.env"


def test_record_discarded_list(entries_with_dupes):
    result = deduplicate(entries_with_dupes, filename="test.env")
    rec = next(r for r in result.records if r.key == "HOST")
    assert len(rec.discarded) == 2


def test_multiple_distinct_duplicates():
    entries = [
        _entry("A", "1", 1),
        _entry("B", "x", 2),
        _entry("A", "2", 3),
        _entry("B", "y", 4),
    ]
    result = deduplicate(entries)
    assert result.total_removed == 2
    assert set(result.affected_keys) == {"A", "B"}

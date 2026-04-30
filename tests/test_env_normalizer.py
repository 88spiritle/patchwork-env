"""Tests for patchwork_env.env_normalizer."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_normalizer import (
    normalize_entries,
    NormalizeRecord,
    NormalizeResult,
)


def _entry(key: str, value: str, comment: str = "") -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=comment, raw_line=f"{key}={value}")


# ---------------------------------------------------------------------------
# NormalizeResult helpers
# ---------------------------------------------------------------------------

class TestNormalizeResult:
    def test_was_clean_when_no_changes(self):
        result = NormalizeResult(filename="a.env", records=[], entries=[])
        assert result.was_clean is True

    def test_total_changed_counts_records_with_changes(self):
        r1 = NormalizeRecord(
            key="FOO", original_key="foo", original_value="bar",
            normalized_key="FOO", normalized_value="bar",
            changes=["key_uppercased"],
        )
        r2 = NormalizeRecord(
            key="BAZ", original_key="BAZ", original_value="qux",
            normalized_key="BAZ", normalized_value="qux",
            changes=[],
        )
        result = NormalizeResult(filename="a.env", records=[r1, r2], entries=[])
        assert result.total_changed == 1
        assert result.was_clean is False


# ---------------------------------------------------------------------------
# normalize_entries — key uppercasing
# ---------------------------------------------------------------------------

def test_lowercase_key_is_uppercased():
    entries = [_entry("database_url", "postgres://localhost/db")]
    result = normalize_entries(entries, filename="test.env")
    assert result.entries[0].key == "DATABASE_URL"


def test_already_uppercase_key_unchanged():
    entries = [_entry("DATABASE_URL", "postgres://localhost/db")]
    result = normalize_entries(entries, filename="test.env")
    assert result.entries[0].key == "DATABASE_URL"
    assert result.records[0].changes == []


def test_uppercase_keys_false_preserves_case():
    entries = [_entry("database_url", "value")]
    result = normalize_entries(entries, filename="test.env", uppercase_keys=False)
    assert result.entries[0].key == "database_url"
    assert result.records[0].changes == []


# ---------------------------------------------------------------------------
# normalize_entries — value whitespace stripping
# ---------------------------------------------------------------------------

def test_value_with_leading_space_is_stripped():
    entries = [_entry("KEY", "  hello  ")]
    result = normalize_entries(entries, filename="test.env")
    assert result.entries[0].value == "hello"
    assert "value_stripped" in result.records[0].changes


def test_clean_value_unchanged():
    entries = [_entry("KEY", "hello")]
    result = normalize_entries(entries, filename="test.env")
    assert result.entries[0].value == "hello"
    assert "value_stripped" not in result.records[0].changes


def test_strip_value_whitespace_false_preserves_spaces():
    entries = [_entry("KEY", "  hello  ")]
    result = normalize_entries(
        entries, filename="test.env", strip_value_whitespace=False
    )
    assert result.entries[0].value == "  hello  "


# ---------------------------------------------------------------------------
# normalize_entries — combined changes
# ---------------------------------------------------------------------------

def test_both_changes_recorded_together():
    entries = [_entry("my_key", "  value  ")]
    result = normalize_entries(entries, filename="test.env")
    record = result.records[0]
    assert "key_uppercased" in record.changes
    assert "value_stripped" in record.changes
    assert result.total_changed == 1


def test_filename_stored_on_result():
    result = normalize_entries([], filename="staging.env")
    assert result.filename == "staging.env"


def test_original_key_preserved_in_record():
    entries = [_entry("my_key", "val")]
    result = normalize_entries(entries, filename="test.env")
    assert result.records[0].original_key == "my_key"


def test_comment_preserved_on_normalized_entry():
    entry = EnvEntry(key="key", value="val", comment="keep me", raw_line="key=val")
    result = normalize_entries([entry], filename="test.env")
    assert result.entries[0].comment == "keep me"

"""Tests for patchwork_env.env_trimmer."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_trimmer import TrimRecord, TrimResult, trim_entries


def _entry(key: str, value: str, raw_line: str = "") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw_line=raw_line, comment=None)


def _blank(raw_line: str = "") -> EnvEntry:
    """Simulate a blank / comment line (key is None)."""
    return EnvEntry(key=None, value=None, raw_line=raw_line, comment=None)


# ---------------------------------------------------------------------------
# TrimRecord
# ---------------------------------------------------------------------------

def test_trim_record_stores_key():
    rec = TrimRecord(key="FOO", original_value=" bar ", trimmed_value="bar")
    assert rec.key == "FOO"


def test_trim_record_stores_values():
    rec = TrimRecord(key="FOO", original_value=" bar ", trimmed_value="bar")
    assert rec.original_value == " bar "
    assert rec.trimmed_value == "bar"


# ---------------------------------------------------------------------------
# TrimResult properties
# ---------------------------------------------------------------------------

def test_was_clean_when_no_records():
    result = TrimResult(filename=".env", entries=[], records=[])
    assert result.was_clean is True


def test_not_clean_when_records_present():
    rec = TrimRecord(key="A", original_value=" v ", trimmed_value="v")
    result = TrimResult(filename=".env", entries=[], records=[rec])
    assert result.was_clean is False


def test_total_trimmed_counts_records():
    records = [
        TrimRecord(key="A", original_value=" x ", trimmed_value="x"),
        TrimRecord(key="B", original_value="\ty\t", trimmed_value="y"),
    ]
    result = TrimResult(filename=".env", entries=[], records=records)
    assert result.total_trimmed == 2


# ---------------------------------------------------------------------------
# trim_entries
# ---------------------------------------------------------------------------

def test_clean_entries_unchanged():
    entries = [_entry("FOO", "bar"), _entry("BAZ", "qux")]
    result = trim_entries(entries, filename=".env")
    assert result.was_clean is True
    assert result.entries[0].value == "bar"
    assert result.entries[1].value == "qux"


def test_leading_whitespace_trimmed():
    entries = [_entry("FOO", "  hello")]
    result = trim_entries(entries)
    assert result.entries[0].value == "hello"
    assert result.total_trimmed == 1


def test_trailing_whitespace_trimmed():
    entries = [_entry("FOO", "hello   ")]
    result = trim_entries(entries)
    assert result.entries[0].value == "hello"


def test_both_sides_trimmed():
    entries = [_entry("KEY", "\t value \t")]
    result = trim_entries(entries)
    assert result.entries[0].value == "value"


def test_blank_lines_passed_through():
    entries = [_blank("# comment"), _entry("A", "1"), _blank("")]
    result = trim_entries(entries)
    assert len(result.entries) == 3
    assert result.entries[0].key is None
    assert result.entries[2].key is None


def test_filename_stored_in_result():
    result = trim_entries([], filename="production.env")
    assert result.filename == "production.env"


def test_record_captures_original_value():
    entries = [_entry("X", " padded ")]
    result = trim_entries(entries)
    assert result.records[0].original_value == " padded "
    assert result.records[0].trimmed_value == "padded"


def test_multiple_dirty_entries_all_recorded():
    entries = [
        _entry("A", " one "),
        _entry("B", "clean"),
        _entry("C", "  three"),
    ]
    result = trim_entries(entries)
    assert result.total_trimmed == 2
    dirty_keys = {r.key for r in result.records}
    assert dirty_keys == {"A", "C"}

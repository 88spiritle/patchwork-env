"""Tests for patchwork_env.env_flattener."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_flattener import (
    FlattenedEntry,
    FlattenResult,
    flatten_entries,
)


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}", line_number=1)


@pytest.fixture
def entries():
    return [
        _entry("APP_HOST", "localhost"),
        _entry("APP_PORT", "8080"),
        _entry("DB_URL", "postgres://localhost/mydb"),
    ]


# ---------------------------------------------------------------------------
# FlattenResult properties
# ---------------------------------------------------------------------------

class TestFlattenResult:
    def test_total_counts_entries(self, entries):
        result = flatten_entries(entries, "test.env")
        assert result.total == 3

    def test_flat_keys_lists_all_keys(self, entries):
        result = flatten_entries(entries, "test.env")
        assert result.flat_keys == ["APP_HOST", "APP_PORT", "DB_URL"]

    def test_total_stripped_zero_without_prefix(self, entries):
        result = flatten_entries(entries, "test.env")
        assert result.total_stripped == 0

    def test_source_file_stored(self, entries):
        result = flatten_entries(entries, "production.env")
        assert result.source_file == "production.env"


# ---------------------------------------------------------------------------
# strip_prefix behaviour
# ---------------------------------------------------------------------------

def test_strip_prefix_removes_matching_prefix(entries):
    result = flatten_entries(entries, "test.env", strip_prefix="APP")
    flat_keys = result.flat_keys
    assert "HOST" in flat_keys
    assert "PORT" in flat_keys


def test_strip_prefix_leaves_non_matching_keys_intact(entries):
    result = flatten_entries(entries, "test.env", strip_prefix="APP")
    assert "DB_URL" in result.flat_keys


def test_strip_prefix_records_stripped_prefix(entries):
    result = flatten_entries(entries, "test.env", strip_prefix="APP")
    stripped = [e for e in result.entries if e.prefix_stripped is not None]
    assert len(stripped) == 2


def test_total_stripped_counts_correctly(entries):
    result = flatten_entries(entries, "test.env", strip_prefix="APP")
    assert result.total_stripped == 2


def test_strip_prefix_case_insensitive():
    e = [_entry("app_debug", "true")]
    result = flatten_entries(e, "test.env", strip_prefix="APP")
    assert result.entries[0].flat_key == "debug"


# ---------------------------------------------------------------------------
# uppercase normalisation
# ---------------------------------------------------------------------------

def test_uppercase_flag_normalises_keys():
    e = [_entry("host", "localhost"), _entry("port", "80")]
    result = flatten_entries(e, "test.env", uppercase=True)
    assert result.flat_keys == ["HOST", "PORT"]


def test_uppercase_combined_with_strip_prefix():
    e = [_entry("app_host", "localhost")]
    result = flatten_entries(e, "test.env", strip_prefix="APP", uppercase=True)
    assert result.flat_keys == ["HOST"]


# ---------------------------------------------------------------------------
# blank / comment entries are skipped
# ---------------------------------------------------------------------------

def test_entries_without_key_are_skipped():
    blank = EnvEntry(key=None, value=None, raw="# comment", line_number=1)
    result = flatten_entries([blank], "test.env")
    assert result.total == 0


# ---------------------------------------------------------------------------
# prefix_used stored on result
# ---------------------------------------------------------------------------

def test_prefix_used_stored_on_result(entries):
    result = flatten_entries(entries, "test.env", strip_prefix="APP")
    assert result.prefix_used == "APP"


def test_prefix_used_none_when_not_provided(entries):
    result = flatten_entries(entries, "test.env")
    assert result.prefix_used is None

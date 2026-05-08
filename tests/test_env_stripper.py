"""Tests for patchwork_env.env_stripper."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_stripper import StripRecord, StripResult, strip_keys


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(
        key=key,
        value=value,
        raw_line=f"{key}={value}",
        comment=None,
        filename="test.env",
    )


@pytest.fixture()
def entries():
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PASSWORD", "secret"),
        _entry("APP_PORT", "8080"),
        _entry("API_KEY", "abc123"),
    ]


# ---------------------------------------------------------------------------
# StripResult properties
# ---------------------------------------------------------------------------

def test_was_clean_when_nothing_stripped(entries):
    result = StripResult(filename="test.env", kept=entries, stripped=[])
    assert result.was_clean is True


def test_not_clean_when_entries_stripped(entries):
    record = StripRecord(key="DB_PASSWORD", value="secret", filename="test.env")
    result = StripResult(filename="test.env", kept=entries[:-1], stripped=[record])
    assert result.was_clean is False


def test_total_stripped_counts_records():
    records = [
        StripRecord(key="A", value="1", filename="f.env"),
        StripRecord(key="B", value="2", filename="f.env"),
    ]
    result = StripResult(filename="f.env", stripped=records)
    assert result.total_stripped == 2


# ---------------------------------------------------------------------------
# strip_keys behaviour
# ---------------------------------------------------------------------------

def test_no_keys_to_remove_keeps_all(entries):
    result = strip_keys(entries, [], filename="test.env")
    assert len(result.kept) == len(entries)
    assert result.total_stripped == 0


def test_single_key_removed(entries):
    result = strip_keys(entries, ["DB_PASSWORD"], filename="test.env")
    kept_keys = [e.key for e in result.kept]
    assert "DB_PASSWORD" not in kept_keys
    assert result.total_stripped == 1


def test_multiple_keys_removed(entries):
    result = strip_keys(entries, ["DB_HOST", "API_KEY"], filename="test.env")
    assert result.total_stripped == 2
    kept_keys = [e.key for e in result.kept]
    assert "DB_HOST" not in kept_keys
    assert "API_KEY" not in kept_keys


def test_removal_is_case_insensitive(entries):
    result = strip_keys(entries, ["db_password"], filename="test.env")
    assert result.total_stripped == 1
    assert result.stripped[0].key == "DB_PASSWORD"


def test_strip_record_stores_value(entries):
    result = strip_keys(entries, ["DB_HOST"], filename="test.env")
    assert result.stripped[0].value == "localhost"


def test_strip_record_stores_filename(entries):
    result = strip_keys(entries, ["APP_PORT"], filename="prod.env")
    assert result.stripped[0].filename == "prod.env"


def test_unknown_key_does_not_strip_anything(entries):
    result = strip_keys(entries, ["NONEXISTENT"], filename="test.env")
    assert result.was_clean is True
    assert len(result.kept) == len(entries)


def test_result_filename_is_propagated(entries):
    result = strip_keys(entries, [], filename="staging.env")
    assert result.filename == "staging.env"

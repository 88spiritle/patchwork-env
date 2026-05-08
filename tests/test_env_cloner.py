"""Tests for patchwork_env.env_cloner."""

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_cloner import CloneRecord, CloneResult, clone_entries


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw_line=f"{key}={value}")


@pytest.fixture()
def source():
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("SECRET_KEY", "abc123"),
    ]


@pytest.fixture()
def target():
    return [
        _entry("DB_HOST", "prod-host"),
        _entry("APP_NAME", "myapp"),
    ]


def test_clone_result_total_cloned(source, target):
    result = clone_entries(source, target)
    assert result.total_cloned == 3


def test_clone_result_filenames(source, target):
    result = clone_entries(source, target, source_filename="a.env", target_filename="b.env")
    assert result.source_filename == "a.env"
    assert result.target_filename == "b.env"


def test_overwrite_counted(source, target):
    result = clone_entries(source, target)
    assert result.total_overwritten == 1  # DB_HOST already exists


def test_was_clean_when_no_overwrites(source):
    result = clone_entries(source, [], overwrite=True)
    assert result.was_clean


def test_no_overwrite_skips_existing(source, target):
    result = clone_entries(source, target, overwrite=False)
    # DB_HOST is in target, so it should be skipped
    keys_cloned = [r.target_key for r in result.records]
    assert "DB_HOST" not in keys_cloned


def test_key_filter_limits_cloned_entries(source, target):
    result = clone_entries(source, target, keys=["DB_HOST", "DB_PORT"])
    assert result.total_cloned == 2
    cloned_keys = {r.source_key for r in result.records}
    assert "SECRET_KEY" not in cloned_keys


def test_key_transform_renames_keys(source):
    result = clone_entries(source, [], key_transform=lambda k: k.replace("DB_", "PG_"))
    target_keys = {r.target_key for r in result.records}
    assert "PG_HOST" in target_keys
    assert "PG_PORT" in target_keys
    assert "SECRET_KEY" in target_keys  # unaffected


def test_source_key_preserved_in_record(source):
    result = clone_entries(source, [], key_transform=lambda k: k + "_COPY")
    for record in result.records:
        assert record.target_key == record.source_key + "_COPY"


def test_value_copied_correctly(source, target):
    result = clone_entries(source, target)
    record_map = {r.source_key: r for r in result.records}
    assert record_map["DB_PORT"].value == "5432"


def test_clone_record_overwritten_flag_true_for_existing(source, target):
    result = clone_entries(source, target)
    record_map = {r.target_key: r for r in result.records}
    assert record_map["DB_HOST"].overwritten is True


def test_clone_record_overwritten_flag_false_for_new(source, target):
    result = clone_entries(source, target)
    record_map = {r.target_key: r for r in result.records}
    assert record_map["SECRET_KEY"].overwritten is False


def test_empty_source_returns_zero_cloned(target):
    result = clone_entries([], target)
    assert result.total_cloned == 0
    assert result.was_clean

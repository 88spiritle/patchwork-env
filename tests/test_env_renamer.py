import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_renamer import rename_key, rename_many, RenameRecord, RenameResult


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=None, raw=f"{key}={value}")


@pytest.fixture
def entries():
    return [_entry("DB_HOST", "localhost"), _entry("DB_PORT", "5432"), _entry("APP_ENV", "prod")]


def test_rename_key_updates_key(entries):
    result = rename_key(entries, "DB_HOST", "DATABASE_HOST")
    keys = [e.key for e in result.entries]
    assert "DATABASE_HOST" in keys
    assert "DB_HOST" not in keys


def test_rename_key_preserves_value(entries):
    result = rename_key(entries, "DB_HOST", "DATABASE_HOST")
    renamed = next(e for e in result.entries if e.key == "DATABASE_HOST")
    assert renamed.value == "localhost"


def test_rename_key_records_change(entries):
    result = rename_key(entries, "DB_PORT", "DATABASE_PORT")
    assert len(result.records) == 1
    assert result.records[0].old_key == "DB_PORT"
    assert result.records[0].new_key == "DATABASE_PORT"


def test_rename_key_missing_key_is_skipped(entries):
    result = rename_key(entries, "MISSING_KEY", "NEW_KEY")
    assert "MISSING_KEY" in result.skipped
    assert result.records == []


def test_rename_key_conflict_is_skipped(entries):
    # DB_PORT already exists, renaming DB_HOST -> DB_PORT should be skipped
    result = rename_key(entries, "DB_HOST", "DB_PORT")
    assert "DB_HOST" in result.skipped
    assert result.records == []


def test_rename_key_entry_count_unchanged(entries):
    result = rename_key(entries, "APP_ENV", "ENVIRONMENT")
    assert len(result.entries) == len(entries)


def test_rename_many_applies_all(entries):
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = rename_many(entries, mapping)
    keys = [e.key for e in result.entries]
    assert "DATABASE_HOST" in keys
    assert "DATABASE_PORT" in keys
    assert "DB_HOST" not in keys
    assert "DB_PORT" not in keys


def test_rename_many_records_all_changes(entries):
    mapping = {"DB_HOST": "DATABASE_HOST", "APP_ENV": "ENVIRONMENT"}
    result = rename_many(entries, mapping)
    assert len(result.records) == 2


def test_rename_many_partial_skip(entries):
    mapping = {"DB_HOST": "DATABASE_HOST", "GHOST": "PHANTOM"}
    result = rename_many(entries, mapping)
    assert len(result.records) == 1
    assert "GHOST" in result.skipped


def test_rename_record_repr():
    r = RenameRecord(old_key="A", new_key="B", value="x")
    assert "A" in repr(r) and "B" in repr(r)

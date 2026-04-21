"""Tests for env_migrator module."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_migrator import (
    MigrationRule,
    MigrationResult,
    migrate_entries,
    _apply_transform,
)


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=None, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# MigrationRule
# ---------------------------------------------------------------------------

def test_migration_rule_repr_no_transform():
    rule = MigrationRule(old_key="OLD", new_key="NEW")
    assert "OLD -> NEW" in repr(rule)
    assert "[" not in repr(rule)


def test_migration_rule_repr_with_transform():
    rule = MigrationRule(old_key="OLD", new_key="NEW", transform="upper")
    assert "[upper]" in repr(rule)


# ---------------------------------------------------------------------------
# _apply_transform
# ---------------------------------------------------------------------------

def test_transform_upper():
    assert _apply_transform("hello", "upper") == "HELLO"


def test_transform_lower():
    assert _apply_transform("HELLO", "lower") == "hello"


def test_transform_none_passthrough():
    assert _apply_transform("Hello", None) == "Hello"


# ---------------------------------------------------------------------------
# migrate_entries
# ---------------------------------------------------------------------------

@pytest.fixture
def entries():
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PASS", "secret"),
        _entry("APP_PORT", "8080"),
    ]


def test_rename_key_is_applied(entries):
    rules = [MigrationRule(old_key="DB_HOST", new_key="DATABASE_HOST")]
    result = migrate_entries(entries, rules, source_file=".env")
    keys = [e.key for e in result.migrated]
    assert "DATABASE_HOST" in keys
    assert "DB_HOST" not in keys


def test_value_preserved_after_rename(entries):
    rules = [MigrationRule(old_key="DB_HOST", new_key="DATABASE_HOST")]
    result = migrate_entries(entries, rules)
    renamed = next(e for e in result.migrated if e.key == "DATABASE_HOST")
    assert renamed.value == "localhost"


def test_transform_applied_to_value(entries):
    rules = [MigrationRule(old_key="DB_PASS", new_key="DB_PASSWORD", transform="upper")]
    result = migrate_entries(entries, rules)
    renamed = next(e for e in result.migrated if e.key == "DB_PASSWORD")
    assert renamed.value == "SECRET"


def test_unmatched_keys_recorded(entries):
    rules = [MigrationRule(old_key="DB_HOST", new_key="DATABASE_HOST")]
    result = migrate_entries(entries, rules)
    assert "DB_PASS" in result.unmatched_keys
    assert "APP_PORT" in result.unmatched_keys


def test_skipped_key_when_rule_has_no_match(entries):
    rules = [MigrationRule(old_key="MISSING_KEY", new_key="NEW_KEY")]
    result = migrate_entries(entries, rules, skip_missing=True)
    assert "MISSING_KEY" in result.skipped_keys


def test_rules_applied_count(entries):
    rules = [
        MigrationRule(old_key="DB_HOST", new_key="DATABASE_HOST"),
        MigrationRule(old_key="DB_PASS", new_key="DB_PASSWORD"),
    ]
    result = migrate_entries(entries, rules)
    assert result.total_migrated == 2


def test_result_repr_contains_source():
    result = MigrationResult(source_file="prod.env")
    assert "prod.env" in repr(result)


def test_empty_rules_returns_all_entries_unchanged(entries):
    result = migrate_entries(entries, [], source_file=".env")
    assert len(result.migrated) == len(entries)
    assert result.total_migrated == 0

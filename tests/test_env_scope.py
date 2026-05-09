"""Tests for env_scope module."""
from __future__ import annotations

import pytest

from patchwork_env.env_scope import ScopeRegistry, ScopeResult
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


@pytest.fixture()
def registry() -> ScopeRegistry:
    return ScopeRegistry()


@pytest.fixture()
def entries() -> list[EnvEntry]:
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("SECRET_KEY", "abc123"),
        _entry("DEBUG", "true"),
    ]


def test_define_creates_record(registry: ScopeRegistry) -> None:
    rec = registry.define("database", ["DB_HOST", "DB_PORT"])
    assert rec.scope == "database"
    assert "DB_HOST" in rec.keys
    assert "DB_PORT" in rec.keys


def test_define_normalises_keys_to_upper(registry: ScopeRegistry) -> None:
    rec = registry.define("ci", ["debug", "secret_key"])
    assert "DEBUG" in rec.keys
    assert "SECRET_KEY" in rec.keys


def test_get_returns_none_for_unknown(registry: ScopeRegistry) -> None:
    assert registry.get("nonexistent") is None


def test_get_returns_record_after_define(registry: ScopeRegistry) -> None:
    registry.define("web", ["DEBUG"])
    assert registry.get("web") is not None


def test_remove_deletes_scope(registry: ScopeRegistry) -> None:
    registry.define("tmp", ["DEBUG"])
    registry.remove("tmp")
    assert registry.get("tmp") is None


def test_remove_missing_scope_is_noop(registry: ScopeRegistry) -> None:
    registry.remove("ghost")  # must not raise


def test_all_scopes_lists_defined(registry: ScopeRegistry) -> None:
    registry.define("a", [])
    registry.define("b", [])
    assert set(registry.all_scopes()) == {"a", "b"}


def test_apply_includes_matching_keys(
    registry: ScopeRegistry, entries: list[EnvEntry]
) -> None:
    registry.define("database", ["DB_HOST", "DB_PORT"])
    result = registry.apply("database", entries, filename="test.env")
    included_keys = [e.key for e in result.included]
    assert "DB_HOST" in included_keys
    assert "DB_PORT" in included_keys


def test_apply_excludes_non_matching_keys(
    registry: ScopeRegistry, entries: list[EnvEntry]
) -> None:
    registry.define("database", ["DB_HOST", "DB_PORT"])
    result = registry.apply("database", entries, filename="test.env")
    excluded_keys = [e.key for e in result.excluded]
    assert "SECRET_KEY" in excluded_keys
    assert "DEBUG" in excluded_keys


def test_apply_unknown_scope_excludes_all(
    registry: ScopeRegistry, entries: list[EnvEntry]
) -> None:
    result = registry.apply("unknown", entries, filename="test.env")
    assert result.total_included == 0
    assert result.total_excluded == len(entries)


def test_result_filename_set(
    registry: ScopeRegistry, entries: list[EnvEntry]
) -> None:
    registry.define("s", ["DEBUG"])
    result = registry.apply("s", entries, filename="prod.env")
    assert result.filename == "prod.env"


def test_result_scope_name_set(
    registry: ScopeRegistry, entries: list[EnvEntry]
) -> None:
    registry.define("myScope", ["DEBUG"])
    result = registry.apply("myScope", entries)
    assert result.scope == "myScope"

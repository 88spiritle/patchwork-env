"""Tests for patchwork_env.differ module."""

import pytest

from patchwork_env.differ import DiffStatus, diff_env_files
from patchwork_env.parser import EnvFile, EnvEntry


def make_env_file(pairs: dict, path: str = "test.env") -> EnvFile:
    entries = [
        EnvEntry(key=k, raw_value=v, comment=None)
        for k, v in pairs.items()
    ]
    return EnvFile(entries=entries, path=path)


@pytest.fixture
def base_env():
    return make_env_file(
        {"APP_ENV": "production", "DB_HOST": "localhost", "SECRET": "abc123"},
        path=".env.base",
    )


@pytest.fixture
def target_env():
    return make_env_file(
        {"APP_ENV": "staging", "DB_HOST": "localhost", "API_KEY": "xyz789"},
        path=".env.target",
    )


def test_diff_names_are_set(base_env, target_env):
    result = diff_env_files(base_env, target_env)
    assert result.base_name == ".env.base"
    assert result.target_name == ".env.target"


def test_modified_key_detected(base_env, target_env):
    result = diff_env_files(base_env, target_env)
    modified_keys = {e.key for e in result.modified}
    assert "APP_ENV" in modified_keys


def test_removed_key_detected(base_env, target_env):
    result = diff_env_files(base_env, target_env)
    removed_keys = {e.key for e in result.removed}
    assert "SECRET" in removed_keys


def test_added_key_detected(base_env, target_env):
    result = diff_env_files(base_env, target_env)
    added_keys = {e.key for e in result.added}
    assert "API_KEY" in added_keys


def test_unchanged_key_detected(base_env, target_env):
    result = diff_env_files(base_env, target_env)
    unchanged_keys = {e.key for e in result.unchanged}
    assert "DB_HOST" in unchanged_keys


def test_has_changes_true(base_env, target_env):
    result = diff_env_files(base_env, target_env)
    assert result.has_changes() is True


def test_has_changes_false_identical():
    env = make_env_file({"FOO": "bar", "BAZ": "qux"})
    result = diff_env_files(env, env)
    assert result.has_changes() is False


def test_all_keys_covered(base_env, target_env):
    result = diff_env_files(base_env, target_env)
    all_keys = {e.key for e in result.entries}
    assert all_keys == {"APP_ENV", "DB_HOST", "SECRET", "API_KEY"}


def test_modified_entry_values(base_env, target_env):
    result = diff_env_files(base_env, target_env)
    modified = {e.key: e for e in result.modified}
    assert modified["APP_ENV"].base_value == "production"
    assert modified["APP_ENV"].target_value == "staging"

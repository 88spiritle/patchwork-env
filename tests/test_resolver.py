"""Tests for patchwork_env.resolver module."""

import pytest

from patchwork_env.differ import EnvDiff
from patchwork_env.parser import EnvEntry, EnvFile
from patchwork_env.resolver import (
    ResolutionStrategy,
    auto_resolve,
    resolve_diff,
)


def make_env_file(name: str, pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v) for k, v in pairs.items()]
    return EnvFile(name=name, entries=entries)


@pytest.fixture
def base_env():
    return make_env_file("base", {"APP_ENV": "production", "DB_HOST": "db.prod", "TIMEOUT": "30"})


@pytest.fixture
def target_env():
    return make_env_file("target", {"APP_ENV": "staging", "DB_HOST": "db.staging", "NEW_KEY": "hello"})


@pytest.fixture
def sample_diff(base_env, target_env):
    return EnvDiff(base=base_env, target=target_env)


def test_resolve_use_target_for_modified(sample_diff):
    resolutions = {"APP_ENV": ResolutionStrategy.USE_TARGET}
    result = resolve_diff(sample_diff, resolutions)
    result_dict = result.as_dict()
    assert result_dict["APP_ENV"] == "staging"


def test_resolve_use_base_for_modified(sample_diff):
    resolutions = {"APP_ENV": ResolutionStrategy.USE_BASE}
    result = resolve_diff(sample_diff, resolutions)
    result_dict = result.as_dict()
    assert result_dict["APP_ENV"] == "production"


def test_resolve_skip_removes_key(sample_diff):
    resolutions = {"APP_ENV": ResolutionStrategy.SKIP}
    result = resolve_diff(sample_diff, resolutions)
    assert "APP_ENV" not in result.as_dict()


def test_resolve_added_key_included_by_default(sample_diff):
    result = resolve_diff(sample_diff, {})
    assert "NEW_KEY" in result.as_dict()
    assert result.as_dict()["NEW_KEY"] == "hello"


def test_resolve_removed_key_excluded_when_use_target(sample_diff):
    # TIMEOUT exists only in base; USE_TARGET default means it won't appear
    result = resolve_diff(sample_diff, {})
    # Default strategy is USE_TARGET; TIMEOUT not in target so it's dropped
    assert "TIMEOUT" not in result.as_dict()


def test_auto_resolve_use_target(sample_diff):
    result = auto_resolve(sample_diff, ResolutionStrategy.USE_TARGET)
    result_dict = result.as_dict()
    assert result_dict.get("APP_ENV") == "staging"
    assert result_dict.get("DB_HOST") == "db.staging"


def test_auto_resolve_use_base(sample_diff):
    result = auto_resolve(sample_diff, ResolutionStrategy.USE_BASE)
    result_dict = result.as_dict()
    assert result_dict.get("APP_ENV") == "production"
    assert result_dict.get("DB_HOST") == "db.prod"


def test_resolved_file_name_is_resolved(sample_diff):
    result = resolve_diff(sample_diff, {})
    assert result.name == "resolved"

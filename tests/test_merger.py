"""Tests for patchwork_env.merger."""

from __future__ import annotations

import pytest

from patchwork_env.differ import EnvDiff
from patchwork_env.merger import merge, merge_to_text
from patchwork_env.parser import EnvEntry, EnvFile
from patchwork_env.resolver import Resolution, ResolutionStrategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_env_file(mapping: dict, path: str = ".env") -> EnvFile:
    entries = [
        EnvEntry(key=k, value=v, comment=None, raw_line=None)
        for k, v in mapping.items()
    ]
    return EnvFile(path=path, entries=entries)


@pytest.fixture()
def base_env() -> EnvFile:
    return make_env_file({"HOST": "localhost", "PORT": "5432", "DEBUG": "true"})


@pytest.fixture()
def target_env() -> EnvFile:
    return make_env_file({"HOST": "prod.example.com", "PORT": "5432", "NEW_KEY": "secret"})


@pytest.fixture()
def sample_diff(base_env: EnvFile, target_env: EnvFile) -> EnvDiff:
    return EnvDiff.from_files(base_env, target_env)


@pytest.fixture()
def sample_resolution(sample_diff: EnvDiff) -> Resolution:
    return Resolution(
        diff=sample_diff,
        strategies={
            "HOST": ResolutionStrategy.USE_TARGET,
            "DEBUG": ResolutionStrategy.REMOVE,
            "NEW_KEY": ResolutionStrategy.USE_TARGET,
        },
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_merge_returns_env_file(base_env, sample_resolution):
    result = merge(base_env, sample_resolution)
    assert isinstance(result, EnvFile)


def test_merge_use_target_overwrites_value(base_env, sample_resolution):
    result = merge(base_env, sample_resolution)
    result_dict = {e.key: e.value for e in result.entries}
    assert result_dict["HOST"] == "prod.example.com"


def test_merge_remove_drops_key(base_env, sample_resolution):
    result = merge(base_env, sample_resolution)
    keys = [e.key for e in result.entries]
    assert "DEBUG" not in keys


def test_merge_keep_base_retains_value(base_env, sample_diff):
    resolution = Resolution(
        diff=sample_diff,
        strategies={"HOST": ResolutionStrategy.KEEP_BASE},
    )
    result = merge(base_env, resolution)
    result_dict = {e.key: e.value for e in result.entries}
    assert result_dict["HOST"] == "localhost"


def test_merge_added_key_included_with_use_target(base_env, sample_resolution):
    result = merge(base_env, sample_resolution)
    keys = [e.key for e in result.entries]
    assert "NEW_KEY" in keys


def test_merge_unchanged_keys_preserved(base_env, sample_resolution):
    result = merge(base_env, sample_resolution)
    result_dict = {e.key: e.value for e in result.entries}
    assert result_dict["PORT"] == "5432"


def test_merge_to_text_returns_string(base_env, sample_resolution):
    text = merge_to_text(base_env, sample_resolution)
    assert isinstance(text, str)
    assert "HOST=prod.example.com" in text
    assert "DEBUG" not in text

"""Tests for patchwork_env.profile_formatter."""
import pytest

from patchwork_env.profiler import EnvProfile, ProfileRegistry
from patchwork_env.profile_formatter import format_profile, format_registry, format_registry_summary


@pytest.fixture()
def sample_profile() -> EnvProfile:
    return EnvProfile("staging", "staging", overrides={"DEBUG": "false", "PORT": "443"})


@pytest.fixture()
def sample_registry(sample_profile: EnvProfile) -> ProfileRegistry:
    reg = ProfileRegistry()
    reg.register(sample_profile)
    reg.register(EnvProfile("dev", "development", overrides={"DEBUG": "true"}))
    return reg


# ---------------------------------------------------------------------------
# format_profile
# ---------------------------------------------------------------------------

def test_format_profile_contains_name(sample_profile: EnvProfile):
    out = format_profile(sample_profile)
    assert "staging" in out


def test_format_profile_contains_environment(sample_profile: EnvProfile):
    out = format_profile(sample_profile)
    assert "staging" in out


def test_format_profile_shows_keys(sample_profile: EnvProfile):
    out = format_profile(sample_profile)
    assert "DEBUG" in out
    assert "PORT" in out


def test_format_profile_shows_values(sample_profile: EnvProfile):
    out = format_profile(sample_profile)
    assert "false" in out
    assert "443" in out


def test_format_profile_empty_overrides():
    p = EnvProfile("empty", "test")
    out = format_profile(p)
    assert "no overrides" in out


# ---------------------------------------------------------------------------
# format_registry
# ---------------------------------------------------------------------------

def test_format_registry_contains_all_profiles(sample_registry: ProfileRegistry):
    out = format_registry(sample_registry)
    assert "staging" in out
    assert "dev" in out


def test_format_registry_empty():
    reg = ProfileRegistry()
    out = format_registry(reg)
    assert "No profiles" in out


# ---------------------------------------------------------------------------
# format_registry_summary
# ---------------------------------------------------------------------------

def test_format_registry_summary_count(sample_registry: ProfileRegistry):
    out = format_registry_summary(sample_registry)
    assert "2" in out


def test_format_registry_summary_names(sample_registry: ProfileRegistry):
    out = format_registry_summary(sample_registry)
    assert "dev" in out
    assert "staging" in out


def test_format_registry_summary_empty():
    reg = ProfileRegistry()
    out = format_registry_summary(reg)
    assert "0" in out

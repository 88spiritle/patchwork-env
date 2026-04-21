"""Tests for patchwork_env.freeze_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.env_freezer import FreezeRegistry, FrozenKey, FreezeResult
from patchwork_env.freeze_formatter import (
    format_frozen_key,
    format_freeze_result,
    format_freeze_summary,
)
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=None, raw_line=f"{key}={value}")


@pytest.fixture()
def registry() -> FreezeRegistry:
    reg = FreezeRegistry()
    reg.freeze("DB_PASS", "s3cret", reason="compliance")
    reg.freeze("API_TOKEN", "tok123")
    return reg


@pytest.fixture()
def result_with_override(registry: FreezeRegistry) -> FreezeResult:
    entries = [_entry("DB_PASS", "wrong"), _entry("API_TOKEN", "tok123")]
    return registry.apply(entries)


# ---------------------------------------------------------------------------
# format_frozen_key
# ---------------------------------------------------------------------------

def test_format_frozen_key_contains_key():
    fk = FrozenKey(key="MY_KEY", frozen_value="val")
    out = format_frozen_key(fk)
    assert "MY_KEY" in out


def test_format_frozen_key_contains_value():
    fk = FrozenKey(key="MY_KEY", frozen_value="val")
    out = format_frozen_key(fk)
    assert "val" in out


def test_format_frozen_key_shows_reason():
    fk = FrozenKey(key="MY_KEY", frozen_value="val", reason="security")
    out = format_frozen_key(fk)
    assert "security" in out


def test_format_frozen_key_no_reason_no_hash():
    fk = FrozenKey(key="MY_KEY", frozen_value="val")
    out = format_frozen_key(fk)
    assert "#" not in out


# ---------------------------------------------------------------------------
# format_freeze_result
# ---------------------------------------------------------------------------

def test_format_freeze_result_contains_header(result_with_override: FreezeResult):
    out = format_freeze_result(result_with_override)
    assert "Freeze Report" in out


def test_format_freeze_result_shows_filename(result_with_override: FreezeResult):
    out = format_freeze_result(result_with_override, filename=".env.prod")
    assert ".env.prod" in out


def test_format_freeze_result_shows_overridden_marker(result_with_override: FreezeResult):
    out = format_freeze_result(result_with_override)
    assert "overridden" in out


def test_format_freeze_result_shows_frozen_count(result_with_override: FreezeResult):
    out = format_freeze_result(result_with_override)
    assert str(result_with_override.total_frozen) in out


def test_format_freeze_result_no_frozen_keys():
    reg = FreezeRegistry()
    entries = [_entry("HOST", "localhost")]
    result = reg.apply(entries)
    out = format_freeze_result(result)
    assert "No frozen keys" in out


# ---------------------------------------------------------------------------
# format_freeze_summary
# ---------------------------------------------------------------------------

def test_format_freeze_summary_empty():
    out = format_freeze_summary([])
    assert "No keys" in out


def test_format_freeze_summary_lists_keys(registry: FreezeRegistry):
    out = format_freeze_summary(registry.all_frozen)
    assert "DB_PASS" in out
    assert "API_TOKEN" in out

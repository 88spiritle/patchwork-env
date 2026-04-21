"""Tests for patchwork_env.env_freezer."""
from __future__ import annotations

import pytest

from patchwork_env.env_freezer import FreezeRegistry, FrozenKey, FreezeResult
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=None, raw_line=f"{key}={value}")


# ---------------------------------------------------------------------------
# FrozenKey
# ---------------------------------------------------------------------------

class TestFrozenKey:
    def test_key_stored(self):
        fk = FrozenKey(key="DB_PASS", frozen_value="secret")
        assert fk.key == "DB_PASS"

    def test_value_stored(self):
        fk = FrozenKey(key="DB_PASS", frozen_value="secret")
        assert fk.frozen_value == "secret"

    def test_reason_defaults_to_none(self):
        fk = FrozenKey(key="K", frozen_value="v")
        assert fk.reason is None

    def test_reason_stored_when_given(self):
        fk = FrozenKey(key="K", frozen_value="v", reason="compliance")
        assert fk.reason == "compliance"


# ---------------------------------------------------------------------------
# FreezeRegistry
# ---------------------------------------------------------------------------

class TestFreezeRegistry:
    def test_freeze_adds_key(self):
        reg = FreezeRegistry()
        reg.freeze("API_KEY", "abc123")
        assert reg.is_frozen("API_KEY")

    def test_unfreeze_removes_key(self):
        reg = FreezeRegistry()
        reg.freeze("API_KEY", "abc123")
        reg.unfreeze("API_KEY")
        assert not reg.is_frozen("API_KEY")

    def test_unfreeze_missing_is_noop(self):
        reg = FreezeRegistry()
        reg.unfreeze("NONEXISTENT")  # should not raise

    def test_get_returns_none_for_unknown(self):
        reg = FreezeRegistry()
        assert reg.get("MISSING") is None

    def test_get_returns_record(self):
        reg = FreezeRegistry()
        reg.freeze("X", "42", reason="test")
        fk = reg.get("X")
        assert fk is not None
        assert fk.frozen_value == "42"

    def test_all_frozen_returns_list(self):
        reg = FreezeRegistry()
        reg.freeze("A", "1")
        reg.freeze("B", "2")
        assert len(reg.all_frozen) == 2


# ---------------------------------------------------------------------------
# FreezeRegistry.apply
# ---------------------------------------------------------------------------

class TestFreezeApply:
    def test_non_frozen_entry_unchanged(self):
        reg = FreezeRegistry()
        entries = [_entry("HOST", "localhost")]
        result = reg.apply(entries)
        assert result.entries[0].value == "localhost"

    def test_frozen_entry_value_enforced(self):
        reg = FreezeRegistry()
        reg.freeze("DB_PASS", "locked_value")
        entries = [_entry("DB_PASS", "other_value")]
        result = reg.apply(entries)
        assert result.entries[0].value == "locked_value"

    def test_skipped_keys_recorded(self):
        reg = FreezeRegistry()
        reg.freeze("DB_PASS", "locked")
        entries = [_entry("DB_PASS", "wrong")]
        result = reg.apply(entries)
        assert "DB_PASS" in result.skipped_keys

    def test_matching_frozen_value_not_skipped(self):
        reg = FreezeRegistry()
        reg.freeze("DB_PASS", "correct")
        entries = [_entry("DB_PASS", "correct")]
        result = reg.apply(entries)
        assert result.skipped_keys == []

    def test_total_frozen_count(self):
        reg = FreezeRegistry()
        reg.freeze("A", "1")
        reg.freeze("B", "2")
        entries = [_entry("A", "x"), _entry("B", "2"), _entry("C", "3")]
        result = reg.apply(entries)
        assert result.total_frozen == 2

    def test_total_skipped_count(self):
        reg = FreezeRegistry()
        reg.freeze("A", "1")
        entries = [_entry("A", "wrong")]
        result = reg.apply(entries)
        assert result.total_skipped == 1

"""Tests for env_locker and lock_formatter."""
from __future__ import annotations

import json

import pytest

from patchwork_env.env_locker import LockedKey, LockRegistry
from patchwork_env.lock_formatter import (
    format_lock_registry,
    format_lock_summary,
    format_locked_key,
)
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str = "x") -> EnvEntry:
    return EnvEntry(key=key, raw_value=value, comment=None, original_line=f"{key}={value}")


# ---------------------------------------------------------------------------
# LockedKey
# ---------------------------------------------------------------------------

class TestLockedKey:
    def test_key_stored(self):
        lk = LockedKey(key="DB_PASS", reason="prod secret")
        assert lk.key == "DB_PASS"

    def test_reason_stored(self):
        lk = LockedKey(key="API_KEY", reason="do not touch")
        assert lk.reason == "do not touch"

    def test_reason_defaults_to_none(self):
        lk = LockedKey(key="FOO", reason=None)
        assert lk.reason is None

    def test_round_trip_dict(self):
        lk = LockedKey(key="SECRET", reason="locked by ci")
        restored = LockedKey.from_dict(lk.to_dict())
        assert restored.key == lk.key
        assert restored.reason == lk.reason
        assert restored.locked_at == lk.locked_at


# ---------------------------------------------------------------------------
# LockRegistry
# ---------------------------------------------------------------------------

class TestLockRegistry:
    def test_starts_empty(self):
        reg = LockRegistry(name="prod")
        assert reg.locked_keys == []

    def test_lock_adds_key(self):
        reg = LockRegistry(name="prod")
        reg.lock("DB_PASS")
        assert reg.is_locked("DB_PASS")

    def test_lock_normalises_to_upper(self):
        reg = LockRegistry(name="prod")
        reg.lock("db_pass")
        assert reg.is_locked("DB_PASS")

    def test_lock_idempotent_updates_reason(self):
        reg = LockRegistry(name="prod")
        reg.lock("KEY", reason="first")
        reg.lock("KEY", reason="second")
        assert reg.get("KEY").reason == "second"
        assert len(reg.locked_keys) == 1

    def test_unlock_removes_key(self):
        reg = LockRegistry(name="prod")
        reg.lock("TOKEN")
        removed = reg.unlock("TOKEN")
        assert removed is True
        assert not reg.is_locked("TOKEN")

    def test_unlock_missing_returns_false(self):
        reg = LockRegistry(name="prod")
        assert reg.unlock("GHOST") is False

    def test_check_entries_returns_locked_keys(self):
        reg = LockRegistry(name="prod")
        reg.lock("SECRET")
        entries = [_entry("SECRET"), _entry("SAFE")]
        hits = reg.check_entries(entries)
        assert hits == ["SECRET"]
        assert "SAFE" not in hits

    def test_round_trip_dict(self):
        reg = LockRegistry(name="staging")
        reg.lock("DB_URL", reason="infra")
        reg.lock("API_KEY")
        restored = LockRegistry.from_dict(reg.to_dict())
        assert restored.name == "staging"
        assert restored.is_locked("DB_URL")
        assert restored.is_locked("API_KEY")


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_locked_key_contains_key():
    lk = LockedKey(key="MY_SECRET", reason=None)
    out = format_locked_key(lk)
    assert "MY_SECRET" in out


def test_format_locked_key_shows_reason():
    lk = LockedKey(key="TOKEN", reason="never change")
    out = format_locked_key(lk)
    assert "never change" in out


def test_format_lock_registry_shows_name():
    reg = LockRegistry(name="production")
    out = format_lock_registry(reg)
    assert "production" in out


def test_format_lock_registry_empty_message():
    reg = LockRegistry(name="dev")
    out = format_lock_registry(reg)
    assert "no locked keys" in out


def test_format_lock_registry_lists_keys():
    reg = LockRegistry(name="prod")
    reg.lock("DB_PASS")
    reg.lock("API_KEY")
    out = format_lock_registry(reg)
    assert "DB_PASS" in out
    assert "API_KEY" in out


def test_format_lock_summary_count():
    reg = LockRegistry(name="prod")
    reg.lock("A")
    reg.lock("B")
    out = format_lock_summary(reg)
    assert "2" in out
    assert "prod" in out

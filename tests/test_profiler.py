"""Tests for patchwork_env.profiler."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.profiler import EnvProfile, ProfileRegistry


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=None, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# EnvProfile
# ---------------------------------------------------------------------------

class TestEnvProfile:
    def test_set_and_override(self):
        p = EnvProfile("dev", "development")
        p.set("DEBUG", "true")
        assert p.overrides["DEBUG"] == "true"

    def test_unset_removes_key(self):
        p = EnvProfile("dev", "development", overrides={"A": "1"})
        p.unset("A")
        assert "A" not in p.overrides

    def test_unset_missing_key_is_noop(self):
        p = EnvProfile("dev", "development")
        p.unset("MISSING")  # should not raise

    def test_apply_overrides_existing_key(self):
        p = EnvProfile("dev", "development", overrides={"PORT": "9000"})
        entries = [_entry("PORT", "8080"), _entry("HOST", "localhost")]
        result = p.apply(entries)
        port_entry = next(e for e in result if e.key == "PORT")
        assert port_entry.value == "9000"

    def test_apply_adds_new_key(self):
        p = EnvProfile("dev", "development", overrides={"NEW_KEY": "val"})
        entries = [_entry("EXISTING", "x")]
        result = p.apply(entries)
        keys = [e.key for e in result]
        assert "NEW_KEY" in keys

    def test_apply_preserves_other_entries(self):
        p = EnvProfile("dev", "development", overrides={"A": "1"})
        entries = [_entry("A", "0"), _entry("B", "2")]
        result = p.apply(entries)
        b_entry = next(e for e in result if e.key == "B")
        assert b_entry.value == "2"

    def test_round_trip_dict(self):
        p = EnvProfile("staging", "staging", overrides={"X": "y"})
        restored = EnvProfile.from_dict(p.to_dict())
        assert restored.name == p.name
        assert restored.environment == p.environment
        assert restored.overrides == p.overrides


# ---------------------------------------------------------------------------
# ProfileRegistry
# ---------------------------------------------------------------------------

class TestProfileRegistry:
    def test_register_and_get(self):
        reg = ProfileRegistry()
        p = EnvProfile("prod", "production")
        reg.register(p)
        assert reg.get("prod") is p

    def test_get_missing_returns_none(self):
        reg = ProfileRegistry()
        assert reg.get("nonexistent") is None

    def test_list_names_sorted(self):
        reg = ProfileRegistry()
        reg.register(EnvProfile("z", "z"))
        reg.register(EnvProfile("a", "a"))
        assert reg.list_names() == ["a", "z"]

    def test_remove_existing(self):
        reg = ProfileRegistry()
        reg.register(EnvProfile("dev", "dev"))
        assert reg.remove("dev") is True
        assert reg.get("dev") is None

    def test_remove_missing_returns_false(self):
        reg = ProfileRegistry()
        assert reg.remove("ghost") is False

    def test_registry_round_trip(self):
        reg = ProfileRegistry()
        reg.register(EnvProfile("ci", "ci", overrides={"CI": "true"}))
        restored = ProfileRegistry.from_dict(reg.to_dict())
        assert restored.list_names() == ["ci"]
        assert restored.get("ci").overrides == {"CI": "true"}

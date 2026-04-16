import pytest
from patchwork_env.env_pinner import PinnedKey, PinRegistry
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=None, raw=f"{key}={value}")


class TestPinRegistry:
    def test_pin_adds_key(self):
        reg = PinRegistry(name="test")
        reg.pin("FOO", "bar")
        assert reg.is_pinned("FOO")

    def test_unpin_removes_key(self):
        reg = PinRegistry(name="test")
        reg.pin("FOO", "bar")
        reg.unpin("FOO")
        assert not reg.is_pinned("FOO")

    def test_unpin_missing_is_noop(self):
        reg = PinRegistry(name="test")
        reg.unpin("MISSING")  # should not raise

    def test_is_pinned_false_for_unknown(self):
        reg = PinRegistry(name="test")
        assert not reg.is_pinned("UNKNOWN")

    def test_apply_overrides_pinned_value(self):
        reg = PinRegistry(name="test")
        reg.pin("FOO", "pinned_value")
        entries = [_entry("FOO", "original"), _entry("BAR", "unchanged")]
        result = reg.apply(entries)
        foo = next(e for e in result if e.key == "FOO")
        bar = next(e for e in result if e.key == "BAR")
        assert foo.value == "pinned_value"
        assert bar.value == "unchanged"

    def test_apply_preserves_unpinned_entries(self):
        reg = PinRegistry(name="test")
        entries = [_entry("A", "1"), _entry("B", "2")]
        result = reg.apply(entries)
        assert [e.key for e in result] == ["A", "B"]

    def test_to_dict_round_trip(self):
        reg = PinRegistry(name="prod")
        reg.pin("SECRET", "abc123", reason="locked by ops")
        data = reg.to_dict()
        restored = PinRegistry.from_dict(data)
        assert restored.name == "prod"
        assert restored.is_pinned("SECRET")
        assert restored.pins["SECRET"].value == "abc123"
        assert restored.pins["SECRET"].reason == "locked by ops"

    def test_from_dict_no_pins(self):
        reg = PinRegistry.from_dict({"name": "empty"})
        assert reg.name == "empty"
        assert len(reg.pins) == 0

    def test_pin_reason_optional(self):
        reg = PinRegistry(name="test")
        reg.pin("KEY", "val")
        assert reg.pins["KEY"].reason is None

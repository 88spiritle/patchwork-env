"""Tests for env_tagger module."""
import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_tagger import TaggedEntry, TagRegistry, apply_tags


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, raw_value=value, comment=None, line_number=1)


class TestTagRegistry:
    def test_tag_adds_tags(self):
        reg = TagRegistry(name="test")
        reg.tag("DB_HOST", "database", "infra")
        assert "database" in reg.tags_for("DB_HOST")
        assert "infra" in reg.tags_for("DB_HOST")

    def test_untag_removes_tag(self):
        reg = TagRegistry(name="test")
        reg.tag("API_KEY", "secret", "auth")
        reg.untag("API_KEY", "secret")
        assert "secret" not in reg.tags_for("API_KEY")
        assert "auth" in reg.tags_for("API_KEY")

    def test_untag_missing_is_noop(self):
        reg = TagRegistry(name="test")
        reg.untag("MISSING", "ghost")  # should not raise

    def test_untag_all_removes_key(self):
        reg = TagRegistry(name="test")
        reg.tag("X", "only")
        reg.untag("X", "only")
        assert reg.tags_for("X") == set()
        assert "X" not in reg.to_dict()["tags"]

    def test_keys_for_tag(self):
        reg = TagRegistry(name="test")
        reg.tag("DB_HOST", "infra")
        reg.tag("DB_PORT", "infra")
        reg.tag("API_KEY", "secret")
        result = reg.keys_for_tag("infra")
        assert set(result) == {"DB_HOST", "DB_PORT"}

    def test_to_dict_round_trip(self):
        reg = TagRegistry(name="prod")
        reg.tag("FOO", "a", "b")
        reg.tag("BAR", "c")
        data = reg.to_dict()
        reg2 = TagRegistry.from_dict(data)
        assert reg2.name == "prod"
        assert reg2.tags_for("FOO") == {"a", "b"}
        assert reg2.tags_for("BAR") == {"c"}

    def test_tags_for_unknown_key_returns_empty(self):
        reg = TagRegistry(name="test")
        assert reg.tags_for("UNKNOWN") == set()


def test_apply_tags_annotates_entries():
    entries = [_entry("DB_HOST"), _entry("API_KEY"), _entry("PORT")]
    reg = TagRegistry(name="test")
    reg.tag("DB_HOST", "infra")
    reg.tag("API_KEY", "secret")
    result = apply_tags(entries, reg)
    assert len(result) == 3
    assert all(isinstance(r, TaggedEntry) for r in result)
    assert result[0].tags == {"infra"}
    assert result[1].tags == {"secret"}
    assert result[2].tags == set()


def test_tagged_entry_repr():
    te = TaggedEntry(entry=_entry("FOO"), tags={"x", "y"})
    r = repr(te)
    assert "FOO" in r
    assert "tags" in r

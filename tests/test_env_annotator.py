"""Tests for patchwork_env.env_annotator."""
import pytest

from patchwork_env.env_annotator import AnnotatedEntry, AnnotationRegistry
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, raw_value=value, comment=None, original_line=f"{key}={value}")


# ---------------------------------------------------------------------------
# AnnotationRegistry
# ---------------------------------------------------------------------------

class TestAnnotationRegistry:
    def test_starts_empty(self):
        reg = AnnotationRegistry(name="test")
        assert reg.annotated_keys() == []

    def test_annotate_stores_text(self):
        reg = AnnotationRegistry(name="test")
        reg.annotate("DB_HOST", "Primary database host")
        assert reg.get("DB_HOST") == "Primary database host"

    def test_key_normalised_to_upper(self):
        reg = AnnotationRegistry(name="test")
        reg.annotate("db_host", "lowercase input")
        assert reg.get("DB_HOST") == "lowercase input"

    def test_annotate_overwrites_existing(self):
        reg = AnnotationRegistry(name="test")
        reg.annotate("KEY", "first")
        reg.annotate("KEY", "second")
        assert reg.get("KEY") == "second"

    def test_remove_deletes_annotation(self):
        reg = AnnotationRegistry(name="test")
        reg.annotate("KEY", "some note")
        reg.remove("KEY")
        assert reg.get("KEY") is None

    def test_remove_missing_is_noop(self):
        reg = AnnotationRegistry(name="test")
        reg.remove("NONEXISTENT")  # must not raise

    def test_get_returns_none_for_missing(self):
        reg = AnnotationRegistry(name="test")
        assert reg.get("MISSING") is None

    def test_annotated_keys_lists_all(self):
        reg = AnnotationRegistry(name="test")
        reg.annotate("A", "note a")
        reg.annotate("B", "note b")
        assert set(reg.annotated_keys()) == {"A", "B"}


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------

def test_apply_returns_annotated_entries():
    reg = AnnotationRegistry(name="test")
    reg.annotate("DB_HOST", "host note")
    entries = [_entry("DB_HOST"), _entry("SECRET_KEY")]
    result = reg.apply(entries)
    assert len(result) == 2
    assert all(isinstance(r, AnnotatedEntry) for r in result)


def test_apply_fills_empty_annotation_for_unannotated():
    reg = AnnotationRegistry(name="test")
    result = reg.apply([_entry("PLAIN")])
    assert result[0].annotation == ""


def test_apply_attaches_correct_annotation():
    reg = AnnotationRegistry(name="test")
    reg.annotate("DB_HOST", "the host")
    result = reg.apply([_entry("DB_HOST")])
    assert result[0].annotation == "the host"


# ---------------------------------------------------------------------------
# serialisation round-trip
# ---------------------------------------------------------------------------

def test_round_trip_dict():
    reg = AnnotationRegistry(name="prod")
    reg.annotate("API_KEY", "third-party API key")
    reg.annotate("DB_URL", "postgres connection string")
    restored = AnnotationRegistry.from_dict(reg.to_dict())
    assert restored.name == "prod"
    assert restored.get("API_KEY") == "third-party API key"
    assert restored.get("DB_URL") == "postgres connection string"


def test_to_dict_structure():
    reg = AnnotationRegistry(name="staging")
    reg.annotate("FOO", "bar")
    d = reg.to_dict()
    assert d["name"] == "staging"
    assert "annotations" in d
    assert d["annotations"]["FOO"] == "bar"

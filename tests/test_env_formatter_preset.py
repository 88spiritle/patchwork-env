"""Tests for env_formatter_preset module."""
import pytest

from patchwork_env.env_formatter_preset import (
    FormatterPreset,
    PresetRegistry,
    build_default_registry,
    DEFAULT_PRESETS,
)


# ---------------------------------------------------------------------------
# FormatterPreset
# ---------------------------------------------------------------------------

class TestFormatterPreset:
    def test_name_stored(self):
        p = FormatterPreset(name="test", description="A test preset")
        assert p.name == "test"

    def test_description_stored(self):
        p = FormatterPreset(name="test", description="A test preset")
        assert p.description == "A test preset"

    def test_defaults(self):
        p = FormatterPreset(name="x", description="y")
        assert p.show_values is True
        assert p.redact_sensitive is False
        assert p.max_value_length is None
        assert p.include_metadata is False
        assert p.color is True
        assert p.tags == []

    def test_tags_stored(self):
        p = FormatterPreset(name="x", description="y", tags=["ci", "audit"])
        assert "ci" in p.tags
        assert "audit" in p.tags


# ---------------------------------------------------------------------------
# PresetRegistry
# ---------------------------------------------------------------------------

@pytest.fixture()
def registry() -> PresetRegistry:
    return PresetRegistry()


@pytest.fixture()
def sample_preset() -> FormatterPreset:
    return FormatterPreset(name="MySample", description="Sample preset")


def test_registry_starts_empty(registry):
    assert len(registry) == 0


def test_register_adds_preset(registry, sample_preset):
    registry.register(sample_preset)
    assert len(registry) == 1


def test_get_returns_preset_case_insensitive(registry, sample_preset):
    registry.register(sample_preset)
    assert registry.get("mysample") is sample_preset
    assert registry.get("MYSAMPLE") is sample_preset


def test_get_missing_returns_none(registry):
    assert registry.get("nonexistent") is None


def test_all_returns_list(registry, sample_preset):
    registry.register(sample_preset)
    result = registry.all()
    assert isinstance(result, list)
    assert sample_preset in result


def test_names_returns_original_case(registry, sample_preset):
    registry.register(sample_preset)
    assert "MySample" in registry.names()


def test_remove_existing_preset(registry, sample_preset):
    registry.register(sample_preset)
    removed = registry.remove("MySample")
    assert removed is True
    assert len(registry) == 0


def test_remove_missing_returns_false(registry):
    assert registry.remove("ghost") is False


# ---------------------------------------------------------------------------
# build_default_registry
# ---------------------------------------------------------------------------

def test_default_registry_has_all_builtin_presets():
    reg = build_default_registry()
    assert len(reg) == len(DEFAULT_PRESETS)


def test_default_registry_contains_safe_preset():
    reg = build_default_registry()
    p = reg.get("safe")
    assert p is not None
    assert p.redact_sensitive is True


def test_default_registry_contains_keys_only_preset():
    reg = build_default_registry()
    p = reg.get("keys-only")
    assert p is not None
    assert p.show_values is False


def test_default_registry_compact_has_max_length():
    reg = build_default_registry()
    p = reg.get("compact")
    assert p is not None
    assert p.max_value_length == 40


def test_default_registry_verbose_includes_metadata():
    reg = build_default_registry()
    p = reg.get("verbose")
    assert p is not None
    assert p.include_metadata is True

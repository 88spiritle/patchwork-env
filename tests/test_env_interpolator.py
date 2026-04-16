"""Tests for patchwork_env.env_interpolator."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_interpolator import interpolate, InterpolatedEntry, InterpolationWarning


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw_line=f"{key}={value}")


def test_plain_value_unchanged():
    entries = [_entry("HOST", "localhost")]
    result = interpolate(entries)
    assert result[0].resolved_value == "localhost"
    assert result[0].warnings == []


def test_single_reference_resolved():
    entries = [_entry("BASE", "http://example.com"), _entry("URL", "${BASE}/api")]
    result = interpolate(entries)
    url_entry = next(r for r in result if r.key == "URL")
    assert url_entry.resolved_value == "http://example.com/api"
    assert url_entry.warnings == []


def test_multiple_references_resolved():
    entries = [
        _entry("PROTO", "https"),
        _entry("HOST", "example.com"),
        _entry("FULL", "${PROTO}://${HOST}"),
    ]
    result = interpolate(entries)
    full = next(r for r in result if r.key == "FULL")
    assert full.resolved_value == "https://example.com"


def test_undefined_reference_warns():
    entries = [_entry("URL", "${MISSING}/path")]
    result = interpolate(entries)
    assert result[0].resolved_value == "${MISSING}/path"
    assert len(result[0].warnings) == 1
    assert result[0].warnings[0].ref == "MISSING"
    assert "undefined" in result[0].warnings[0].message


def test_self_referential_warns():
    entries = [_entry("X", "${X}_suffix")]
    result = interpolate(entries)
    assert result[0].resolved_value == "${X}_suffix"
    assert any("self-referential" in w.message for w in result[0].warnings)


def test_extra_mapping_used():
    entries = [_entry("GREETING", "Hello ${NAME}")]
    result = interpolate(entries, extra={"NAME": "World"})
    assert result[0].resolved_value == "Hello World"
    assert result[0].warnings == []


def test_extra_overrides_entry():
    entries = [_entry("VAR", "original"), _entry("OUT", "${VAR}")]
    result = interpolate(entries, extra={"VAR": "overridden"})
    out = next(r for r in result if r.key == "OUT")
    assert out.resolved_value == "overridden"


def test_returns_interpolated_entry_instances():
    entries = [_entry("A", "1")]
    result = interpolate(entries)
    assert isinstance(result[0], InterpolatedEntry)
    assert result[0].key == "A"


def test_no_entries_returns_empty():
    assert interpolate([]) == []

"""Tests for env_version module."""
from __future__ import annotations

import pytest

from patchwork_env.env_version import VersionEntry, VersionHistory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _history(name: str = "production") -> VersionHistory:
    return VersionHistory(name=name)


# ---------------------------------------------------------------------------
# VersionHistory.add
# ---------------------------------------------------------------------------

def test_add_returns_version_entry():
    h = _history()
    entry = h.add(label="initial", filename=".env", key_count=5)
    assert isinstance(entry, VersionEntry)


def test_add_increments_version():
    h = _history()
    e1 = h.add("first", ".env", 3)
    e2 = h.add("second", ".env.prod", 4)
    assert e1.version == 1
    assert e2.version == 2


def test_add_stores_label_and_filename():
    h = _history()
    e = h.add(label="release-1.0", filename=".env.prod", key_count=10)
    assert e.label == "release-1.0"
    assert e.filename == ".env.prod"


def test_add_stores_key_count():
    h = _history()
    e = h.add("v1", ".env", key_count=7)
    assert e.key_count == 7


def test_add_stores_notes_when_provided():
    h = _history()
    e = h.add("v1", ".env", 2, notes="hotfix")
    assert e.notes == "hotfix"


def test_add_notes_defaults_to_none():
    h = _history()
    e = h.add("v1", ".env", 2)
    assert e.notes is None


def test_add_timestamp_is_set():
    h = _history()
    e = h.add("v1", ".env", 2)
    assert e.timestamp  # non-empty string


# ---------------------------------------------------------------------------
# VersionHistory.latest / get
# ---------------------------------------------------------------------------

def test_latest_returns_none_when_empty():
    h = _history()
    assert h.latest() is None


def test_latest_returns_last_added():
    h = _history()
    h.add("first", ".env", 3)
    e2 = h.add("second", ".env", 4)
    assert h.latest() is e2


def test_get_returns_correct_version():
    h = _history()
    h.add("first", ".env", 3)
    h.add("second", ".env", 4)
    result = h.get(1)
    assert result is not None
    assert result.label == "first"


def test_get_returns_none_for_missing_version():
    h = _history()
    assert h.get(99) is None


# ---------------------------------------------------------------------------
# Round-trip serialisation
# ---------------------------------------------------------------------------

def test_version_entry_round_trip():
    h = _history()
    h.add("v1", ".env", 5, notes="initial")
    h.add("v2", ".env.prod", 8)
    data = h.to_dict()
    restored = VersionHistory.from_dict(data)
    assert restored.name == h.name
    assert len(restored.entries) == 2
    assert restored.entries[0].label == "v1"
    assert restored.entries[1].key_count == 8


def test_to_dict_contains_expected_keys():
    h = _history()
    h.add("v1", ".env", 3)
    d = h.to_dict()
    assert "name" in d
    assert "entries" in d
    entry_d = d["entries"][0]
    for key in ("version", "label", "filename", "key_count", "timestamp", "notes"):
        assert key in entry_d

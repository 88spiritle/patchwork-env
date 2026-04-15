"""Tests for patchwork_env.exporter."""

from __future__ import annotations

import json
import textwrap
from unittest.mock import MagicMock

import pytest

from patchwork_env.exporter import (
    export_diff_json,
    export_diff_patch,
    export_snapshot_dotenv,
    export_snapshot_json,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_entry(key: str, raw_value: str, comment: str = "") -> MagicMock:
    e = MagicMock()
    e.key = key
    e.raw_value = raw_value
    e.comment = comment
    return e


def _make_snapshot(entries: list) -> MagicMock:
    snap = MagicMock()
    snap.entries = entries
    snap.to_dict.return_value = {
        "environment": "staging",
        "entries": [{"key": e.key, "value": e.raw_value} for e in entries],
    }
    return snap


def _make_diff_entry(key, old=None, new=None):
    e = MagicMock()
    e.key = key
    e.old_value = old
    e.new_value = new
    return e


def _make_report(env="staging", added=(), removed=(), modified=(), unchanged=()):
    r = MagicMock()
    r.environment = env
    r.added = list(added)
    r.removed = list(removed)
    r.modified = list(modified)
    r.unchanged = list(unchanged)
    return r


# ---------------------------------------------------------------------------
# export_snapshot_json
# ---------------------------------------------------------------------------

def test_export_snapshot_json_is_valid_json():
    snap = _make_snapshot([_make_entry("FOO", "bar")])
    result = export_snapshot_json(snap)
    parsed = json.loads(result)
    assert "environment" in parsed


def test_export_snapshot_json_indent():
    snap = _make_snapshot([])
    result = export_snapshot_json(snap, indent=4)
    # 4-space indent means lines start with four spaces
    assert "    " in result


# ---------------------------------------------------------------------------
# export_snapshot_dotenv
# ---------------------------------------------------------------------------

def test_export_snapshot_dotenv_basic():
    entries = [_make_entry("DB_HOST", "localhost"), _make_entry("PORT", "5432")]
    snap = _make_snapshot(entries)
    result = export_snapshot_dotenv(snap)
    assert "DB_HOST=localhost" in result
    assert "PORT=5432" in result


def test_export_snapshot_dotenv_ends_with_newline():
    snap = _make_snapshot([_make_entry("X", "1")])
    assert export_snapshot_dotenv(snap).endswith("\n")


def test_export_snapshot_dotenv_empty():
    snap = _make_snapshot([])
    assert export_snapshot_dotenv(snap) == ""


# ---------------------------------------------------------------------------
# export_diff_json
# ---------------------------------------------------------------------------

def test_export_diff_json_structure():
    report = _make_report(
        added=[_make_diff_entry("NEW_KEY", new="val")],
        removed=[_make_diff_entry("OLD_KEY", old="gone")],
    )
    data = json.loads(export_diff_json(report))
    assert data["environment"] == "staging"
    assert "NEW_KEY" in data["added"]
    assert "OLD_KEY" in data["removed"]


def test_export_diff_json_modified_shape():
    mod = _make_diff_entry("SECRET", old="abc", new="xyz")
    report = _make_report(modified=[mod])
    data = json.loads(export_diff_json(report))
    assert data["modified"][0] == {"key": "SECRET", "old": "abc", "new": "xyz"}


# ---------------------------------------------------------------------------
# export_diff_patch
# ---------------------------------------------------------------------------

def test_export_diff_patch_contains_header():
    report = _make_report(env="production")
    assert "production" in export_diff_patch(report)


def test_export_diff_patch_added_prefix():
    report = _make_report(added=[_make_diff_entry("FOO", new="bar")])
    assert "+ FOO=bar" in export_diff_patch(report)


def test_export_diff_patch_removed_prefix():
    report = _make_report(removed=[_make_diff_entry("BAZ", old="qux")])
    assert "- BAZ=qux" in export_diff_patch(report)


def test_export_diff_patch_modified_shows_both():
    mod = _make_diff_entry("TOKEN", old="old_tok", new="new_tok")
    patch = export_diff_patch(_make_report(modified=[mod]))
    assert "- TOKEN=old_tok" in patch
    assert "+ TOKEN=new_tok" in patch

"""Tests for env_archiver module."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from patchwork_env.env_archiver import Archive, ArchiveEntry, load_archive, save_archive
from patchwork_env.snapshot import Snapshot
from patchwork_env.parser import EnvEntry


def _make_snapshot(filename: str = "prod.env", keys: list[str] | None = None) -> Snapshot:
    keys = keys or ["HOST", "PORT"]
    entries = [EnvEntry(key=k, value="val", raw=f"{k}=val", comment="", line_number=i + 1) for i, k in enumerate(keys)]
    snap = Snapshot(filename=filename, entries=entries)
    return snap


# ---------------------------------------------------------------------------
# ArchiveEntry
# ---------------------------------------------------------------------------

def test_archive_entry_repr():
    snap = _make_snapshot()
    entry = ArchiveEntry(timestamp="2024-01-01T00:00:00+00:00", label="v1", snapshot=snap)
    assert "v1" in repr(entry)


def test_archive_entry_round_trip():
    snap = _make_snapshot()
    entry = ArchiveEntry(timestamp="2024-01-01T00:00:00+00:00", label="release-1", snapshot=snap)
    restored = ArchiveEntry.from_dict(entry.to_dict())
    assert restored.label == entry.label
    assert restored.timestamp == entry.timestamp
    assert restored.snapshot.filename == snap.filename


# ---------------------------------------------------------------------------
# Archive
# ---------------------------------------------------------------------------

def test_archive_starts_empty():
    archive = Archive(name="test-archive")
    assert archive.entries == []
    assert archive.latest() is None


def test_add_returns_entry():
    archive = Archive(name="test-archive")
    snap = _make_snapshot()
    entry = archive.add(snap, label="first")
    assert isinstance(entry, ArchiveEntry)
    assert entry.label == "first"


def test_add_appends_entry():
    archive = Archive(name="test-archive")
    archive.add(_make_snapshot(), label="a")
    archive.add(_make_snapshot(), label="b")
    assert len(archive.entries) == 2


def test_latest_returns_last():
    archive = Archive(name="test-archive")
    archive.add(_make_snapshot(), label="first")
    archive.add(_make_snapshot(), label="second")
    assert archive.latest().label == "second"


def test_find_returns_matching_entry():
    archive = Archive(name="test-archive")
    archive.add(_make_snapshot(), label="alpha")
    archive.add(_make_snapshot(), label="beta")
    found = archive.find("alpha")
    assert found is not None
    assert found.label == "alpha"


def test_find_returns_none_for_missing():
    archive = Archive(name="test-archive")
    assert archive.find("nonexistent") is None


def test_archive_round_trip_dict():
    archive = Archive(name="my-archive")
    archive.add(_make_snapshot(), label="snap-1")
    archive.add(_make_snapshot(keys=["DB_URL"]), label="snap-2")
    restored = Archive.from_dict(archive.to_dict())
    assert restored.name == archive.name
    assert len(restored.entries) == 2
    assert restored.entries[1].label == "snap-2"


# ---------------------------------------------------------------------------
# save / load
# ---------------------------------------------------------------------------

def test_save_and_load_archive(tmp_path):
    path = str(tmp_path / "archive.json")
    archive = Archive(name="persist-test")
    archive.add(_make_snapshot(), label="v0.1")
    save_archive(archive, path)
    loaded = load_archive(path)
    assert loaded.name == "persist-test"
    assert loaded.latest().label == "v0.1"


def test_saved_archive_is_valid_json(tmp_path):
    path = str(tmp_path / "archive.json")
    archive = Archive(name="json-check")
    archive.add(_make_snapshot(), label="check")
    save_archive(archive, path)
    with open(path) as fh:
        data = json.load(fh)
    assert "entries" in data

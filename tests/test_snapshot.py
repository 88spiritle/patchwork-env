"""Tests for snapshot capture, persistence, and listing."""
import json
import os
import tempfile
from pathlib import Path

import pytest

from patchwork_env.snapshot import Snapshot, list_snapshots, load_snapshot, save_snapshot


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "prod.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n")
    return str(p)


def test_capture_returns_snapshot(env_file):
    snap = Snapshot.capture(env_file, "production")
    assert snap.environment == "production"
    assert snap.filepath == env_file
    assert isinstance(snap.captured_at, str)
    assert len(snap.entries) == 3


def test_capture_entry_keys(env_file):
    snap = Snapshot.capture(env_file, "production")
    keys = [e["key"] for e in snap.entries]
    assert "DB_HOST" in keys
    assert "SECRET" in keys


def test_entry_map(env_file):
    snap = Snapshot.capture(env_file, "production")
    m = snap.entry_map()
    assert m["DB_HOST"] == "localhost"
    assert m["DB_PORT"] == "5432"


def test_round_trip_dict(env_file):
    snap = Snapshot.capture(env_file, "staging")
    restored = Snapshot.from_dict(snap.to_dict())
    assert restored.environment == snap.environment
    assert restored.entries == snap.entries


def test_save_and_load(env_file, tmp_path):
    snap = Snapshot.capture(env_file, "staging")
    path = save_snapshot(snap, str(tmp_path / "store"))
    assert os.path.isfile(path)
    loaded = load_snapshot(path)
    assert loaded.environment == "staging"
    assert loaded.entries == snap.entries


def test_list_snapshots_empty(tmp_path):
    result = list_snapshots(str(tmp_path / "nonexistent"))
    assert result == []


def test_list_snapshots_filtered(env_file, tmp_path):
    store = str(tmp_path / "store")
    snap1 = Snapshot.capture(env_file, "prod")
    snap2 = Snapshot.capture(env_file, "staging")
    save_snapshot(snap1, store)
    save_snapshot(snap2, store)
    prod_snaps = list_snapshots(store, environment="prod")
    assert all("prod_" in os.path.basename(p) for p in prod_snaps)
    assert len(prod_snaps) == 1

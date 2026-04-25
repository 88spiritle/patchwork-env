"""Tests for env_baseline module."""
import pytest

from patchwork_env.env_baseline import (
    Baseline,
    BaselineEntry,
    BaselineDrift,
    capture_baseline,
    detect_drift,
)
from patchwork_env.snapshot import Snapshot
from patchwork_env.parser import EnvEntry


def _snap(filename: str, pairs: dict) -> Snapshot:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return Snapshot(filename=filename, entries=entries)


# ------------------------------------------------------------------
class TestBaselineEntry:
    def test_round_trip(self):
        be = BaselineEntry(key="DB_HOST", value="localhost", source="prod.env")
        assert BaselineEntry.from_dict(be.to_dict()) == be

    def test_to_dict_keys(self):
        be = BaselineEntry(key="X", value="1", source="f.env")
        d = be.to_dict()
        assert set(d.keys()) == {"key", "value", "source"}


class TestBaseline:
    def test_capture_baseline_entry_count(self):
        snap = _snap("prod.env", {"A": "1", "B": "2", "C": "3"})
        b = capture_baseline(snap, name="v1")
        assert len(b.entries) == 3

    def test_capture_baseline_name(self):
        snap = _snap("prod.env", {"A": "1"})
        b = capture_baseline(snap, name="release-1")
        assert b.name == "release-1"

    def test_capture_baseline_source(self):
        snap = _snap("prod.env", {"A": "1"})
        b = capture_baseline(snap, name="v1")
        assert b.entries[0].source == "prod.env"

    def test_entry_map_keys(self):
        snap = _snap("prod.env", {"FOO": "bar", "BAZ": "qux"})
        b = capture_baseline(snap, name="v1")
        assert set(b.entry_map.keys()) == {"FOO", "BAZ"}

    def test_round_trip_dict(self):
        snap = _snap("prod.env", {"X": "y"})
        b = capture_baseline(snap, name="test")
        b2 = Baseline.from_dict(b.to_dict())
        assert b2.name == b.name
        assert len(b2.entries) == len(b.entries)


class TestDetectDrift:
    def test_no_drift_when_identical(self):
        snap = _snap("prod.env", {"A": "1", "B": "2"})
        b = capture_baseline(snap, name="v1")
        drifts = detect_drift(b, snap)
        assert drifts == []

    def test_detects_changed_value(self):
        snap1 = _snap("prod.env", {"A": "1"})
        b = capture_baseline(snap1, name="v1")
        snap2 = _snap("prod.env", {"A": "999"})
        drifts = detect_drift(b, snap2)
        assert len(drifts) == 1
        assert drifts[0].status == "changed"
        assert drifts[0].key == "A"

    def test_detects_removed_key(self):
        snap1 = _snap("prod.env", {"A": "1", "B": "2"})
        b = capture_baseline(snap1, name="v1")
        snap2 = _snap("prod.env", {"A": "1"})
        drifts = detect_drift(b, snap2)
        assert any(d.key == "B" and d.status == "removed" for d in drifts)

    def test_detects_added_key(self):
        snap1 = _snap("prod.env", {"A": "1"})
        b = capture_baseline(snap1, name="v1")
        snap2 = _snap("prod.env", {"A": "1", "NEW": "val"})
        drifts = detect_drift(b, snap2)
        assert any(d.key == "NEW" and d.status == "added" for d in drifts)

    def test_drifts_sorted_by_key(self):
        snap1 = _snap("prod.env", {"Z": "1", "A": "2"})
        b = capture_baseline(snap1, name="v1")
        snap2 = _snap("prod.env", {"Z": "changed", "A": "changed"})
        drifts = detect_drift(b, snap2)
        keys = [d.key for d in drifts]
        assert keys == sorted(keys)

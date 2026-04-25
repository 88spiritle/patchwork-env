"""Tests for baseline_formatter module."""
import pytest

from patchwork_env.env_baseline import (
    Baseline,
    BaselineEntry,
    BaselineDrift,
    capture_baseline,
    detect_drift,
)
from patchwork_env.baseline_formatter import (
    format_baseline,
    format_drift_report,
    format_drift_summary,
)
from patchwork_env.snapshot import Snapshot
from patchwork_env.parser import EnvEntry


def _snap(filename: str, pairs: dict) -> Snapshot:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return Snapshot(filename=filename, entries=entries)


@pytest.fixture
def sample_baseline() -> Baseline:
    snap = _snap("prod.env", {"DB_HOST": "localhost", "PORT": "5432"})
    return capture_baseline(snap, name="v1.0")


def test_format_baseline_contains_name(sample_baseline):
    out = format_baseline(sample_baseline)
    assert "v1.0" in out


def test_format_baseline_shows_keys(sample_baseline):
    out = format_baseline(sample_baseline)
    assert "DB_HOST" in out
    assert "PORT" in out


def test_format_baseline_shows_values(sample_baseline):
    out = format_baseline(sample_baseline)
    assert "localhost" in out
    assert "5432" in out


def test_format_drift_report_no_drift(sample_baseline):
    snap = _snap("prod.env", {"DB_HOST": "localhost", "PORT": "5432"})
    drifts = detect_drift(sample_baseline, snap)
    out = format_drift_report(drifts, sample_baseline.name, snap.filename)
    assert "No drift" in out


def test_format_drift_report_shows_changed():
    snap1 = _snap("prod.env", {"A": "old"})
    b = capture_baseline(snap1, name="v1")
    snap2 = _snap("prod.env", {"A": "new"})
    drifts = detect_drift(b, snap2)
    out = format_drift_report(drifts, b.name, snap2.filename)
    assert "A" in out
    assert "old" in out
    assert "new" in out


def test_format_drift_report_shows_added():
    snap1 = _snap("prod.env", {})
    b = capture_baseline(snap1, name="v1")
    snap2 = _snap("prod.env", {"NEWKEY": "val"})
    drifts = detect_drift(b, snap2)
    out = format_drift_report(drifts, b.name, snap2.filename)
    assert "NEWKEY" in out


def test_format_drift_report_shows_removed():
    snap1 = _snap("prod.env", {"GONE": "bye"})
    b = capture_baseline(snap1, name="v1")
    snap2 = _snap("prod.env", {})
    drifts = detect_drift(b, snap2)
    out = format_drift_report(drifts, b.name, snap2.filename)
    assert "GONE" in out


def test_format_drift_summary_no_drift():
    out = format_drift_summary([])
    assert "No drift" in out


def test_format_drift_summary_counts():
    drifts = [
        BaselineDrift("A", "x", None, "removed"),
        BaselineDrift("B", None, "y", "added"),
        BaselineDrift("C", "old", "new", "changed"),
    ]
    out = format_drift_summary(drifts)
    assert "+1" in out
    assert "-1" in out
    assert "~1" in out

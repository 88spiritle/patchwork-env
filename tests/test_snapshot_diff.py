"""Tests for snapshot diffing and formatting."""
import pytest

from patchwork_env.snapshot import Snapshot
from patchwork_env.snapshot_diff import SnapshotDiffReport, diff_snapshots
from patchwork_env.snapshot_formatter import format_snapshot_diff, format_snapshot_summary


def _make_snapshot(env: str, mapping: dict) -> Snapshot:
    entries = [{"key": k, "value": v, "comment": None} for k, v in mapping.items()]
    return Snapshot(
        environment=env,
        filepath=f"/fake/{env}.env",
        captured_at="2024-01-01T00:00:00+00:00",
        entries=entries,
    )


@pytest.fixture
def old_snap():
    return _make_snapshot("prod", {"DB_HOST": "old-host", "DB_PORT": "5432", "REMOVED": "gone"})


@pytest.fixture
def new_snap():
    return _make_snapshot("prod", {"DB_HOST": "new-host", "DB_PORT": "5432", "ADDED": "here"})


def test_diff_detects_modified(old_snap, new_snap):
    report = diff_snapshots(old_snap, new_snap)
    assert any(e.key == "DB_HOST" and e.status == "modified" for e in report.entries)


def test_diff_detects_added(old_snap, new_snap):
    report = diff_snapshots(old_snap, new_snap)
    assert any(e.key == "ADDED" and e.status == "added" for e in report.entries)


def test_diff_detects_removed(old_snap, new_snap):
    report = diff_snapshots(old_snap, new_snap)
    assert any(e.key == "REMOVED" and e.status == "removed" for e in report.entries)


def test_diff_detects_unchanged(old_snap, new_snap):
    report = diff_snapshots(old_snap, new_snap)
    assert any(e.key == "DB_PORT" and e.status == "unchanged" for e in report.entries)


def test_has_changes_true(old_snap, new_snap):
    report = diff_snapshots(old_snap, new_snap)
    assert report.has_changes() is True


def test_has_changes_false():
    snap = _make_snapshot("prod", {"A": "1"})
    snap2 = _make_snapshot("prod", {"A": "1"})
    report = diff_snapshots(snap, snap2)
    assert report.has_changes() is False


def test_format_diff_contains_env(old_snap, new_snap):
    report = diff_snapshots(old_snap, new_snap)
    text = format_snapshot_diff(report, use_color=False)
    assert "prod" in text


def test_format_diff_no_changes():
    snap = _make_snapshot("dev", {"KEY": "val"})
    snap2 = _make_snapshot("dev", {"KEY": "val"})
    report = diff_snapshots(snap, snap2)
    text = format_snapshot_diff(report, use_color=False)
    assert "No changes" in text


def test_format_summary_counts(old_snap, new_snap):
    report = diff_snapshots(old_snap, new_snap)
    summary = format_snapshot_summary(report)
    assert "+1" in summary
    assert "-1" in summary
    assert "~1" in summary

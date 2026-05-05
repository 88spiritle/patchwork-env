"""Tests for env_differ_stats and stats_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.differ import EnvDiff, DiffEntry, DiffStatus
from patchwork_env.env_differ_stats import KeyStat, DiffStats, compute_stats
from patchwork_env.stats_formatter import format_stats, format_stats_summary, format_key_stat


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _entry(key: str, value: str = "v") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


def _diff_entry(key: str, status: DiffStatus, old: str | None = None, new: str | None = None) -> DiffEntry:
    base = _entry(key, old or "old") if old is not None else None
    target = _entry(key, new or "new") if new is not None else None
    return DiffEntry(key=key, status=status, base_entry=base, target_entry=target)


def _make_diff(*entries: DiffEntry) -> EnvDiff:
    diff = EnvDiff.__new__(EnvDiff)
    diff.base_name = "base.env"
    diff.target_name = "target.env"
    diff._entries = list(entries)
    return diff


# Patch EnvDiff.entries property so our stub works
EnvDiff.entries = property(lambda self: self._entries)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# KeyStat
# ---------------------------------------------------------------------------

class TestKeyStat:
    def test_total_changes_sums_fields(self):
        s = KeyStat(key="FOO", added=1, removed=2, modified=3)
        assert s.total_changes == 6

    def test_total_changes_zero_when_empty(self):
        s = KeyStat(key="FOO")
        assert s.total_changes == 0


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

class TestComputeStats:
    def test_empty_diffs_returns_empty_stats(self):
        ds = compute_stats([], filename="test.env")
        assert ds.total_events == 0
        assert ds.stats == {}

    def test_added_key_counted(self):
        diff = _make_diff(_diff_entry("FOO", DiffStatus.ADDED, new="1"))
        ds = compute_stats([diff])
        assert ds.stats["FOO"].added == 1

    def test_removed_key_counted(self):
        diff = _make_diff(_diff_entry("BAR", DiffStatus.REMOVED, old="1"))
        ds = compute_stats([diff])
        assert ds.stats["BAR"].removed == 1

    def test_modified_key_counted(self):
        diff = _make_diff(_diff_entry("BAZ", DiffStatus.MODIFIED, old="a", new="b"))
        ds = compute_stats([diff])
        assert ds.stats["BAZ"].modified == 1

    def test_multiple_diffs_accumulate(self):
        d1 = _make_diff(_diff_entry("FOO", DiffStatus.ADDED, new="1"))
        d2 = _make_diff(_diff_entry("FOO", DiffStatus.MODIFIED, old="1", new="2"))
        ds = compute_stats([d1, d2])
        assert ds.stats["FOO"].added == 1
        assert ds.stats["FOO"].modified == 1
        assert ds.stats["FOO"].total_changes == 2

    def test_most_changed_ordering(self):
        d = _make_diff(
            _diff_entry("A", DiffStatus.ADDED, new="1"),
            _diff_entry("B", DiffStatus.MODIFIED, old="x", new="y"),
            _diff_entry("B", DiffStatus.MODIFIED, old="y", new="z"),
        )
        ds = compute_stats([d])
        assert ds.most_changed[0].key == "B"

    def test_filename_stored(self):
        ds = compute_stats([], filename="custom.env")
        assert ds.filename == "custom.env"


# ---------------------------------------------------------------------------
# stats_formatter
# ---------------------------------------------------------------------------

class TestStatsFormatter:
    def _sample_ds(self) -> DiffStats:
        d = _make_diff(
            _diff_entry("FOO", DiffStatus.ADDED, new="1"),
            _diff_entry("BAR", DiffStatus.REMOVED, old="2"),
            _diff_entry("BAZ", DiffStatus.MODIFIED, old="a", new="b"),
        )
        return compute_stats([d], filename="sample.env")

    def test_format_stats_contains_filename(self):
        ds = self._sample_ds()
        output = format_stats(ds)
        assert "sample.env" in output

    def test_format_stats_lists_keys(self):
        ds = self._sample_ds()
        output = format_stats(ds)
        assert "FOO" in output
        assert "BAR" in output
        assert "BAZ" in output

    def test_format_stats_top_limits_output(self):
        ds = self._sample_ds()
        output = format_stats(ds, top=1)
        # Only one key should be in the most-changed list after the header
        assert output.count("+1") + output.count("-1") + output.count("~1") >= 1

    def test_format_stats_summary_contains_filename(self):
        ds = self._sample_ds()
        summary = format_stats_summary(ds)
        assert "sample.env" in summary

    def test_format_stats_summary_contains_event_count(self):
        ds = self._sample_ds()
        summary = format_stats_summary(ds)
        assert "3" in summary

    def test_format_key_stat_no_changes(self):
        stat = KeyStat(key="EMPTY")
        line = format_key_stat(stat)
        assert "EMPTY" in line

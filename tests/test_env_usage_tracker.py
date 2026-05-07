"""Tests for env_usage_tracker."""
from __future__ import annotations

import pytest

from patchwork_env.env_usage_tracker import UsageRecord, UsageReport, UsageTracker


def _entry_key(key: str, source: str = "test.env") -> UsageRecord:
    return UsageRecord(key=key, source_file=source)


class TestUsageRecord:
    def test_key_stored(self):
        r = _entry_key("DB_HOST")
        assert r.key == "DB_HOST"

    def test_access_count_defaults_to_one(self):
        r = _entry_key("DB_HOST")
        assert r.access_count == 1

    def test_round_trip_dict(self):
        r = _entry_key("API_KEY")
        r2 = UsageRecord.from_dict(r.to_dict())
        assert r2.key == r.key
        assert r2.source_file == r.source_file
        assert r2.access_count == r.access_count

    def test_to_dict_has_expected_keys(self):
        r = _entry_key("SECRET")
        d = r.to_dict()
        assert set(d.keys()) == {"key", "source_file", "accessed_at", "access_count"}


class TestUsageTracker:
    def test_track_adds_record(self):
        t = UsageTracker()
        t.track("DB_HOST", "prod.env")
        report = t.report("prod.env")
        assert report.total_tracked == 1

    def test_track_normalises_key_to_upper(self):
        t = UsageTracker()
        t.track("db_host", "prod.env")
        report = t.report("prod.env")
        assert report.records[0].key == "DB_HOST"

    def test_track_increments_count_on_repeated_access(self):
        t = UsageTracker()
        t.track("TOKEN", "prod.env")
        t.track("TOKEN", "prod.env")
        report = t.report("prod.env")
        assert report.records[0].access_count == 2

    def test_untrack_removes_key(self):
        t = UsageTracker()
        t.track("TOKEN", "prod.env")
        t.untrack("TOKEN")
        report = t.report("prod.env")
        assert report.total_tracked == 0

    def test_untrack_missing_is_noop(self):
        t = UsageTracker()
        t.untrack("NONEXISTENT")  # should not raise

    def test_reset_clears_all(self):
        t = UsageTracker()
        t.track("A", "f.env")
        t.track("B", "f.env")
        t.reset()
        assert t.report("f.env").total_tracked == 0


class TestUsageReport:
    def test_unused_keys_empty_when_all_accessed(self):
        t = UsageTracker()
        t.track("KEY", "f.env")
        report = t.report("f.env")
        # access_count starts at 1, so none are unused
        assert report.unused_keys == []

    def test_most_used_returns_highest_count(self):
        t = UsageTracker()
        t.track("A", "f.env")
        t.track("B", "f.env")
        t.track("B", "f.env")
        report = t.report("f.env")
        assert report.most_used is not None
        assert report.most_used.key == "B"

    def test_most_used_none_when_empty(self):
        report = UsageReport(source_file="empty.env")
        assert report.most_used is None

    def test_get_returns_record_by_key(self):
        t = UsageTracker()
        t.track("DB_URL", "f.env")
        report = t.report("f.env")
        rec = report.get("db_url")
        assert rec is not None
        assert rec.key == "DB_URL"

    def test_get_returns_none_for_missing_key(self):
        report = UsageReport(source_file="f.env")
        assert report.get("MISSING") is None

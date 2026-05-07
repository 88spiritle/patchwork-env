"""Tests for usage_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.env_usage_tracker import UsageRecord, UsageReport, UsageTracker
from patchwork_env.usage_formatter import format_usage_record, format_usage_report, format_usage_summary


def _record(key: str, count: int = 1) -> UsageRecord:
    r = UsageRecord(key=key, source_file="test.env")
    r.access_count = count
    return r


def _report(keys_counts: list) -> UsageReport:
    report = UsageReport(source_file="sample.env")
    report.records = [_record(k, c) for k, c in keys_counts]
    return report


class TestFormatUsageRecord:
    def test_contains_key(self):
        line = format_usage_record(_record("DB_HOST"))
        assert "DB_HOST" in line

    def test_shows_access_count(self):
        line = format_usage_record(_record("API_KEY", count=5))
        assert "5" in line

    def test_unused_shows_unused_label(self):
        line = format_usage_record(_record("UNUSED_KEY", count=0))
        assert "unused" in line

    def test_active_record_shows_active_label(self):
        line = format_usage_record(_record("ACTIVE_KEY", count=3))
        assert "active" in line


class TestFormatUsageReport:
    def test_contains_filename(self):
        r = _report([("KEY_A", 2)])
        out = format_usage_report(r)
        assert "sample.env" in out

    def test_shows_all_keys(self):
        r = _report([("KEY_A", 1), ("KEY_B", 3)])
        out = format_usage_report(r)
        assert "KEY_A" in out
        assert "KEY_B" in out

    def test_empty_report_shows_no_tracked_message(self):
        r = UsageReport(source_file="empty.env")
        out = format_usage_report(r)
        assert "No tracked keys" in out

    def test_shows_total_tracked(self):
        r = _report([("A", 1), ("B", 2)])
        out = format_usage_report(r)
        assert "Total tracked: 2" in out


class TestFormatUsageSummary:
    def test_contains_filename(self):
        r = _report([("X", 1)])
        line = format_usage_summary(r)
        assert "sample.env" in line

    def test_shows_tracked_count(self):
        r = _report([("A", 1), ("B", 2)])
        line = format_usage_summary(r)
        assert "2 tracked" in line

    def test_shows_top_key(self):
        r = _report([("LOW", 1), ("HIGH", 10)])
        line = format_usage_summary(r)
        assert "HIGH" in line

    def test_top_is_na_when_empty(self):
        r = UsageReport(source_file="empty.env")
        line = format_usage_summary(r)
        assert "n/a" in line

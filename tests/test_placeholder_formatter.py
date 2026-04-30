"""Tests for patchwork_env.placeholder_formatter."""
from patchwork_env.env_placeholder import PlaceholderHit, PlaceholderReport
from patchwork_env.placeholder_formatter import (
    format_placeholder_report,
    format_placeholder_summary,
)


def _report_with_hits(*keys: str) -> PlaceholderReport:
    r = PlaceholderReport(filename="test.env")
    for k in keys:
        r.hits.append(PlaceholderHit(key=k, value="CHANGEME", matched_pattern="CHANGEME"))
    return r


class TestFormatPlaceholderReport:
    def test_contains_filename(self):
        r = _report_with_hits()
        out = format_placeholder_report(r)
        assert "test.env" in out

    def test_clean_report_shows_checkmark(self):
        r = _report_with_hits()
        out = format_placeholder_report(r)
        assert "No placeholder" in out

    def test_hit_shows_key(self):
        r = _report_with_hits("API_KEY")
        out = format_placeholder_report(r)
        assert "API_KEY" in out

    def test_hit_shows_pattern(self):
        r = _report_with_hits("TOKEN")
        out = format_placeholder_report(r)
        assert "CHANGEME" in out

    def test_multiple_hits_all_shown(self):
        r = _report_with_hits("A", "B", "C")
        out = format_placeholder_report(r)
        for key in ("A", "B", "C"):
            assert key in out


class TestFormatPlaceholderSummary:
    def test_shows_file_count(self):
        reports = [_report_with_hits(), _report_with_hits("X")]
        out = format_placeholder_summary(reports)
        assert "2" in out

    def test_shows_total_hits(self):
        reports = [_report_with_hits("A", "B"), _report_with_hits()]
        out = format_placeholder_summary(reports)
        assert "2" in out

    def test_shows_affected_count(self):
        reports = [_report_with_hits("A"), _report_with_hits()]
        out = format_placeholder_summary(reports)
        assert "1" in out

    def test_empty_reports_list(self):
        out = format_placeholder_summary([])
        assert "0" in out

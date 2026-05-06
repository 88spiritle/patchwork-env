"""Tests for patchwork_env.review_formatter."""
from __future__ import annotations

from patchwork_env.env_reviewer import ReviewReport, ReviewFlag
from patchwork_env.review_formatter import format_review_report, format_review_summary


def _report(filename: str = "test.env") -> ReviewReport:
    r = ReviewReport(filename=filename)
    r.flags.append(ReviewFlag("API_KEY", "Sensitive key has empty value.", "error"))
    r.flags.append(ReviewFlag("db_host", "Key is not uppercase.", "warning"))
    r.flags.append(ReviewFlag("DB_HOST", "Classified as 'database'.", "info"))
    return r


def test_format_report_contains_filename():
    output = format_review_report(_report("staging.env"))
    assert "staging.env" in output


def test_format_report_shows_error_key():
    output = format_review_report(_report())
    assert "API_KEY" in output


def test_format_report_shows_warning_key():
    output = format_review_report(_report())
    assert "db_host" in output


def test_format_report_shows_failed_status():
    output = format_review_report(_report())
    assert "FAILED" in output


def test_format_report_shows_passed_status():
    r = ReviewReport(filename="clean.env")
    output = format_review_report(r)
    assert "PASSED" in output


def test_format_report_no_issues_message():
    r = ReviewReport(filename="clean.env")
    output = format_review_report(r)
    assert "No issues" in output


def test_format_report_shows_error_count():
    output = format_review_report(_report())
    assert "Errors: 1" in output


def test_format_report_shows_warning_count():
    output = format_review_report(_report())
    assert "Warnings: 1" in output


def test_format_summary_contains_totals():
    reports = [_report("a.env"), ReviewReport(filename="b.env")]
    output = format_review_summary(reports)
    assert "2" in output  # total files
    assert "Passed" in output or "passed" in output.lower()


def test_format_summary_failed_count():
    reports = [_report("a.env"), ReviewReport(filename="b.env")]
    output = format_review_summary(reports)
    # one report has errors, one is clean
    assert "1" in output

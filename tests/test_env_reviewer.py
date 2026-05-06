"""Tests for patchwork_env.env_reviewer."""
from __future__ import annotations

import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_reviewer import review_entries, ReviewReport, ReviewFlag


def _entry(key: str, value: str = "somevalue", comment: str = "") -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=comment, raw=f"{key}={value}")


# ------------------------------------------------------------------ helpers

class TestReviewReport:
    def test_passed_when_no_errors(self):
        report = ReviewReport(filename="test.env")
        assert report.passed is True

    def test_failed_when_error_present(self):
        report = ReviewReport(filename="test.env")
        report.flags.append(ReviewFlag("KEY", "bad", "error"))
        assert report.passed is False

    def test_errors_filters_correctly(self):
        report = ReviewReport(filename="test.env")
        report.flags.append(ReviewFlag("A", "msg", "error"))
        report.flags.append(ReviewFlag("B", "msg", "warning"))
        assert len(report.errors) == 1
        assert len(report.warnings) == 1

    def test_infos_filters_correctly(self):
        report = ReviewReport(filename="test.env")
        report.flags.append(ReviewFlag("A", "msg", "info"))
        assert len(report.infos) == 1


# ------------------------------------------------------------------ review_entries

def test_empty_entries_passes():
    report = review_entries([], filename="empty.env")
    assert report.passed
    assert report.filename == "empty.env"


def test_clean_entry_has_no_errors():
    entries = [_entry("DATABASE_URL", "postgres://localhost/db")]
    report = review_entries(entries)
    assert report.passed
    assert len(report.errors) == 0


def test_duplicate_key_raises_error():
    entries = [_entry("API_KEY", "abc"), _entry("API_KEY", "xyz")]
    report = review_entries(entries)
    assert not report.passed
    dup_errors = [f for f in report.errors if "Duplicate" in f.message]
    assert len(dup_errors) == 1


def test_placeholder_value_raises_warning():
    entries = [_entry("SECRET", "<your-secret-here>")]
    report = review_entries(entries)
    placeholder_warnings = [f for f in report.warnings if "placeholder" in f.message]
    assert len(placeholder_warnings) >= 1


def test_sensitive_empty_value_raises_error():
    entries = [_entry("API_KEY", "")]
    report = review_entries(entries)
    sensitive_errors = [f for f in report.errors if "empty value" in f.message]
    assert len(sensitive_errors) >= 1


def test_lowercase_key_raises_warning():
    entries = [_entry("my_key", "val")]
    report = review_entries(entries)
    lower_warnings = [f for f in report.warnings if "uppercase" in f.message]
    assert len(lower_warnings) >= 1


def test_entries_without_key_are_skipped():
    entry = EnvEntry(key=None, value=None, comment="# just a comment", raw="# just a comment")
    report = review_entries([entry])
    assert report.passed


def test_classification_info_present():
    entries = [_entry("DB_HOST", "localhost")]
    report = review_entries(entries)
    info_flags = [f for f in report.infos if "Classified" in f.message]
    assert len(info_flags) >= 1


def test_filename_stored():
    report = review_entries([], filename="prod.env")
    assert report.filename == "prod.env"

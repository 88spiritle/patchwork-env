"""Tests for env_inspector and inspection_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_inspector import inspect_entries, InspectionReport
from patchwork_env.inspection_formatter import format_inspection, format_inspection_summary


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


@pytest.fixture
def entries():
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("SECRET", ""),
        _entry("DB_HOST", "remotehost"),  # duplicate
    ]


@pytest.fixture
def raw_lines():
    return [
        "# database config",
        "DB_HOST=localhost",
        "",
        "DB_PORT=5432",
        "SECRET=",
        "DB_HOST=remotehost",
    ]


def test_total_keys(entries, raw_lines):
    report = inspect_entries(entries, filename=".env", raw_lines=raw_lines)
    assert report.total_keys == 4


def test_blank_lines_counted(entries, raw_lines):
    report = inspect_entries(entries, filename=".env", raw_lines=raw_lines)
    assert report.blank_lines == 1


def test_comment_lines_counted(entries, raw_lines):
    report = inspect_entries(entries, filename=".env", raw_lines=raw_lines)
    assert report.comment_lines == 1


def test_empty_value_detected(entries, raw_lines):
    report = inspect_entries(entries, filename=".env", raw_lines=raw_lines)
    assert "SECRET" in report.empty_values
    assert report.has_empty_values is True


def test_duplicate_key_detected(entries, raw_lines):
    report = inspect_entries(entries, filename=".env", raw_lines=raw_lines)
    assert "DB_HOST" in report.duplicate_keys
    assert report.has_duplicates is True


def test_no_duplicates_when_unique():
    e = [_entry("A"), _entry("B")]
    report = inspect_entries(e, filename=".env")
    assert report.has_duplicates is False


def test_longest_key():
    e = [_entry("TINY"), _entry("VERY_LONG_KEY_NAME")]
    report = inspect_entries(e, filename=".env")
    assert report.longest_key == "VERY_LONG_KEY_NAME"


def test_longest_value_key():
    e = [_entry("A", "short"), _entry("B", "a_very_long_value_string")]
    report = inspect_entries(e, filename=".env")
    assert report.longest_value_key == "B"


def test_filename_stored():
    report = inspect_entries([], filename="prod.env")
    assert report.filename == "prod.env"


def test_format_inspection_contains_filename(entries, raw_lines):
    report = inspect_entries(entries, filename="test.env", raw_lines=raw_lines)
    output = format_inspection(report)
    assert "test.env" in output


def test_format_inspection_shows_total_keys(entries, raw_lines):
    report = inspect_entries(entries, filename="test.env", raw_lines=raw_lines)
    output = format_inspection(report)
    assert "4" in output


def test_format_inspection_flags_empty_value(entries, raw_lines):
    report = inspect_entries(entries, filename="test.env", raw_lines=raw_lines)
    output = format_inspection(report)
    assert "SECRET" in output


def test_format_summary_shows_file_count():
    r1 = InspectionReport(filename="a.env", total_keys=3, blank_lines=0, comment_lines=0)
    r2 = InspectionReport(filename="b.env", total_keys=5, blank_lines=1, comment_lines=2)
    output = format_inspection_summary([r1, r2])
    assert "2" in output
    assert "8" in output

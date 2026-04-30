"""Tests for patchwork_env.env_placeholder."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_placeholder import (
    is_placeholder,
    scan_placeholders,
    PlaceholderHit,
    PlaceholderReport,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, comment=None, raw="")


# ---------------------------------------------------------------------------
# is_placeholder
# ---------------------------------------------------------------------------

class TestIsPlaceholder:
    def test_changeme_is_placeholder(self):
        assert is_placeholder("CHANGEME") is True

    def test_angle_bracket_is_placeholder(self):
        assert is_placeholder("<your-secret>") is True

    def test_todo_is_placeholder(self):
        assert is_placeholder("TODO") is True

    def test_normal_value_is_not_placeholder(self):
        assert is_placeholder("mysecretvalue123") is False

    def test_empty_string_is_not_placeholder(self):
        assert is_placeholder("") is False

    def test_example_is_placeholder(self):
        assert is_placeholder("example_token") is True

    def test_case_insensitive(self):
        assert is_placeholder("replace_me") is True


# ---------------------------------------------------------------------------
# scan_placeholders
# ---------------------------------------------------------------------------

class TestScanPlaceholders:
    def test_empty_entries_returns_no_hits(self):
        report = scan_placeholders([], filename="test.env")
        assert not report.has_placeholders

    def test_clean_entries_returns_no_hits(self):
        entries = [_entry("DB_URL", "postgres://localhost/db")]
        report = scan_placeholders(entries, filename="test.env")
        assert not report.has_placeholders

    def test_placeholder_entry_is_detected(self):
        entries = [_entry("API_KEY", "CHANGEME")]
        report = scan_placeholders(entries, filename="test.env")
        assert report.has_placeholders
        assert "API_KEY" in report.placeholder_keys

    def test_filename_is_stored(self):
        report = scan_placeholders([], filename="prod.env")
        assert report.filename == "prod.env"

    def test_matched_pattern_recorded(self):
        entries = [_entry("SECRET", "<fill-in>")]
        report = scan_placeholders(entries, filename="x.env")
        assert report.hits[0].matched_pattern == "<"

    def test_multiple_placeholders_detected(self):
        entries = [
            _entry("A", "CHANGEME"),
            _entry("B", "real_value"),
            _entry("C", "TODO"),
        ]
        report = scan_placeholders(entries, filename="x.env")
        assert len(report.hits) == 2

    def test_entry_without_key_is_skipped(self):
        blank = EnvEntry(key=None, value=None, comment="# comment", raw="# comment")
        report = scan_placeholders([blank], filename="x.env")
        assert not report.has_placeholders

    def test_placeholder_keys_property(self):
        entries = [_entry("TOKEN", "REPLACE_ME"), _entry("HOST", "localhost")]
        report = scan_placeholders(entries, filename="x.env")
        assert report.placeholder_keys == ["TOKEN"]

"""Tests for patchwork_env.env_masker."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_masker import (
    mask_value,
    mask_entries,
    MaskedEntry,
    MaskReport,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw_line=f"{key}={value}")


# ---------------------------------------------------------------------------
# mask_value
# ---------------------------------------------------------------------------

class TestMaskValue:
    def test_long_value_keeps_last_four(self):
        result = mask_value("supersecret")
        assert result.endswith("cret")

    def test_long_value_masks_prefix(self):
        result = mask_value("supersecret")
        assert result.startswith("*")
        assert "*" * 7 == result[:7]

    def test_short_value_fully_masked(self):
        assert mask_value("abc") == "***"

    def test_exact_visible_length_fully_masked(self):
        assert mask_value("abcd", visible=4) == "****"

    def test_custom_visible(self):
        result = mask_value("password123", visible=3)
        assert result.endswith("123")
        assert result.count("*") == len("password123") - 3

    def test_empty_string(self):
        assert mask_value("") == ""


# ---------------------------------------------------------------------------
# mask_entries / MaskReport
# ---------------------------------------------------------------------------

@pytest.fixture()
def entries():
    return [
        _entry("APP_NAME", "myapp"),
        _entry("DB_PASSWORD", "s3cr3tP@ss"),
        _entry("API_KEY", "abc123xyz"),
        _entry("DEBUG", "true"),
    ]


@pytest.fixture()
def report(entries):
    return mask_entries(entries, filename=".env.production")


def test_report_filename_stored(report):
    assert report.filename == ".env.production"


def test_report_entry_count(report, entries):
    assert len(report.entries) == len(entries)


def test_sensitive_count(report):
    # DB_PASSWORD and API_KEY are sensitive
    assert report.sensitive_count == 2


def test_plain_count(report):
    # APP_NAME and DEBUG are plain
    assert report.plain_count == 2


def test_sensitive_value_is_masked(report):
    pw_entry = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert pw_entry.was_sensitive is True
    assert "*" in pw_entry.masked_value
    assert pw_entry.masked_value != pw_entry.original_value


def test_plain_value_unchanged(report):
    app_entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert app_entry.was_sensitive is False
    assert app_entry.masked_value == app_entry.original_value


def test_masked_entry_repr():
    e = MaskedEntry(key="SECRET", original_value="val", masked_value="***", was_sensitive=True)
    r = repr(e)
    assert "SECRET" in r
    assert "***" in r


def test_empty_entries_produces_empty_report():
    r = mask_entries([], filename="empty.env")
    assert isinstance(r, MaskReport)
    assert r.entries == []
    assert r.sensitive_count == 0

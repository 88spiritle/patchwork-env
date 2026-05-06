"""Tests for env_censor.py and censor_formatter.py."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_censor import (
    is_censored_key,
    censor_entries,
    CensoredEntry,
    CensorReport,
)
from patchwork_env.censor_formatter import format_censor_report, format_censor_summary


def _entry(key: str, value: str = "some_value") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# is_censored_key
# ---------------------------------------------------------------------------

class TestIsCensoredKey:
    def test_password_is_censored(self):
        assert is_censored_key("DB_PASSWORD") is True

    def test_token_is_censored(self):
        assert is_censored_key("GITHUB_TOKEN") is True

    def test_api_key_is_censored(self):
        assert is_censored_key("STRIPE_API_KEY") is True

    def test_plain_key_is_not_censored(self):
        assert is_censored_key("APP_PORT") is False

    def test_case_insensitive(self):
        assert is_censored_key("db_password") is True

    def test_custom_blocklist(self):
        assert is_censored_key("MY_CUSTOM", blocklist=["CUSTOM"]) is True
        assert is_censored_key("MY_CUSTOM", blocklist=["NOPE"]) is False


# ---------------------------------------------------------------------------
# censor_entries / CensorReport
# ---------------------------------------------------------------------------

@pytest.fixture()
def entries():
    return [
        _entry("APP_NAME", "myapp"),
        _entry("DB_PASSWORD", "s3cr3t"),
        _entry("PORT", "8080"),
        _entry("API_KEY", "abc123"),
    ]


@pytest.fixture()
def report(entries):
    return censor_entries(entries, filename=".env.prod")


def test_report_filename_set(report):
    assert report.filename == ".env.prod"


def test_total_equals_entry_count(report):
    assert report.total == 4


def test_censored_count_correct(report):
    # DB_PASSWORD and API_KEY should be censored
    assert report.censored_count == 2


def test_plain_entry_not_censored(report):
    app_name = next(e for e in report.entries if e.key == "APP_NAME")
    assert app_name.censored is False
    assert app_name.display_value == "myapp"


def test_sensitive_entry_is_censored(report):
    pwd = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert pwd.censored is True
    assert pwd.display_value == ""


def test_repr_censored(report):
    pwd = next(e for e in report.entries if e.key == "DB_PASSWORD")
    assert "[CENSORED]" in repr(pwd)


def test_repr_plain(report):
    port = next(e for e in report.entries if e.key == "PORT")
    assert "[CENSORED]" not in repr(port)


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_format_report_contains_filename(report):
    out = format_censor_report(report)
    assert ".env.prod" in out


def test_format_report_shows_censored_label(report):
    out = format_censor_report(report)
    assert "CENSORED" in out


def test_format_report_shows_plain_key(report):
    out = format_censor_report(report)
    assert "APP_NAME" in out


def test_format_summary_contains_filename(report):
    out = format_censor_summary(report)
    assert ".env.prod" in out


def test_format_summary_shows_ratio(report):
    out = format_censor_summary(report)
    assert "2/4" in out

"""Tests for patchwork_env.redact_formatter."""

from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_redactor import redact_entries, RedactedEntry, REDACTED_PLACEHOLDER
from patchwork_env.redact_formatter import format_redacted_entries, format_redact_summary


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


@pytest.fixture()
def sample_entries() -> list[RedactedEntry]:
    raw = [
        _entry("APP_ENV", "production"),
        _entry("DB_PASSWORD", "s3cr3t"),
        _entry("PORT", "8080"),
    ]
    return redact_entries(raw)


# ---------------------------------------------------------------------------
# format_redacted_entries
# ---------------------------------------------------------------------------

def test_format_contains_header(sample_entries):
    out = format_redacted_entries(sample_entries, filename=".env")
    assert "Redacted view" in out


def test_format_shows_filename(sample_entries):
    out = format_redacted_entries(sample_entries, filename="prod.env")
    assert "prod.env" in out


def test_format_shows_plain_key_and_value(sample_entries):
    out = format_redacted_entries(sample_entries)
    assert "APP_ENV" in out
    assert "production" in out


def test_format_shows_redacted_placeholder(sample_entries):
    out = format_redacted_entries(sample_entries)
    assert REDACTED_PLACEHOLDER in out


def test_format_sensitive_key_present(sample_entries):
    out = format_redacted_entries(sample_entries)
    assert "DB_PASSWORD" in out


def test_format_sensitive_tag_shown(sample_entries):
    out = format_redacted_entries(sample_entries)
    assert "sensitive" in out


def test_format_empty_entries_shows_no_entries_message():
    out = format_redacted_entries([])
    assert "no entries" in out


# ---------------------------------------------------------------------------
# format_redact_summary
# ---------------------------------------------------------------------------

def test_summary_shows_total(sample_entries):
    out = format_redact_summary(sample_entries)
    assert "3" in out


def test_summary_shows_redacted_count(sample_entries):
    out = format_redact_summary(sample_entries)
    # 1 sensitive key (DB_PASSWORD)
    assert "1" in out


def test_summary_shows_visible_count(sample_entries):
    out = format_redact_summary(sample_entries)
    # 2 visible keys
    assert "2" in out

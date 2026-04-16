"""Tests for patchwork_env.env_redactor."""

from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_redactor import (
    is_sensitive,
    redact_entries,
    REDACTED_PLACEHOLDER,
)


def _entry(key: str, value: str = "some_value") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# is_sensitive
# ---------------------------------------------------------------------------

class TestIsSensitive:
    def test_password_is_sensitive(self):
        assert is_sensitive("DB_PASSWORD") is True

    def test_token_is_sensitive(self):
        assert is_sensitive("GITHUB_TOKEN") is True

    def test_api_key_is_sensitive(self):
        assert is_sensitive("STRIPE_API_KEY") is True

    def test_plain_key_is_not_sensitive(self):
        assert is_sensitive("APP_ENV") is False

    def test_case_insensitive_match(self):
        assert is_sensitive("db_password") is True

    def test_custom_patterns_override_defaults(self):
        # Only "INTERNAL" is sensitive with custom patterns
        assert is_sensitive("INTERNAL_FLAG", patterns={"INTERNAL"}) is True
        # PASSWORD no longer matches
        assert is_sensitive("DB_PASSWORD", patterns={"INTERNAL"}) is False


# ---------------------------------------------------------------------------
# redact_entries
# ---------------------------------------------------------------------------

class TestRedactEntries:
    def test_sensitive_value_is_replaced(self):
        entries = [_entry("DB_PASSWORD", "s3cr3t")]
        result = redact_entries(entries)
        assert result[0].value == REDACTED_PLACEHOLDER
        assert result[0].redacted is True

    def test_plain_value_is_preserved(self):
        entries = [_entry("APP_ENV", "production")]
        result = redact_entries(entries)
        assert result[0].value == "production"
        assert result[0].redacted is False

    def test_original_entry_is_retained(self):
        entry = _entry("DB_PASSWORD", "s3cr3t")
        result = redact_entries([entry])
        assert result[0].original_entry is entry

    def test_empty_input_returns_empty_list(self):
        assert redact_entries([]) == []

    def test_custom_placeholder(self):
        entries = [_entry("SECRET_KEY", "abc")]
        result = redact_entries(entries, placeholder="<hidden>")
        assert result[0].value == "<hidden>"

    def test_entry_without_key_is_skipped(self):
        blank = EnvEntry(key=None, value=None, raw="# comment")
        result = redact_entries([blank])
        assert result == []

    def test_mixed_entries(self):
        entries = [
            _entry("APP_ENV", "staging"),
            _entry("DB_PASSWORD", "hunter2"),
            _entry("PORT", "8080"),
            _entry("API_KEY", "xyz"),
        ]
        result = redact_entries(entries)
        assert result[0].redacted is False
        assert result[1].redacted is True
        assert result[2].redacted is False
        assert result[3].redacted is True

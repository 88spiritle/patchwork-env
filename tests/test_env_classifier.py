"""Tests for patchwork_env.env_classifier."""
from __future__ import annotations

import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_classifier import (
    Category,
    classify_key,
    classify_entries,
    ClassifiedEntry,
    ClassificationReport,
)


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# classify_key
# ---------------------------------------------------------------------------

class TestClassifyKey:
    def test_db_prefix(self):
        assert classify_key("DB_HOST") == Category.DATABASE

    def test_postgres_in_key(self):
        assert classify_key("POSTGRES_PASSWORD") == Category.DATABASE

    def test_jwt_is_auth(self):
        assert classify_key("JWT_SECRET") == Category.AUTH

    def test_api_key_is_auth(self):
        assert classify_key("API_KEY") == Category.AUTH

    def test_port_is_network(self):
        assert classify_key("PORT") == Category.NETWORK

    def test_url_is_network(self):
        assert classify_key("BASE_URL") == Category.NETWORK

    def test_log_prefix_is_logging(self):
        assert classify_key("LOG_LEVEL") == Category.LOGGING

    def test_debug_is_logging(self):
        assert classify_key("DEBUG") == Category.LOGGING

    def test_feature_flag_prefix(self):
        assert classify_key("FEATURE_DARK_MODE") == Category.FEATURE_FLAG

    def test_enable_prefix(self):
        assert classify_key("ENABLE_SIGNUP") == Category.FEATURE_FLAG

    def test_s3_is_storage(self):
        assert classify_key("S3_BUCKET") == Category.STORAGE

    def test_unknown_is_misc(self):
        assert classify_key("APP_NAME") == Category.MISC


# ---------------------------------------------------------------------------
# classify_entries
# ---------------------------------------------------------------------------

class TestClassifyEntries:
    def test_returns_classification_report(self):
        result = classify_entries([], filename="test.env")
        assert isinstance(result, ClassificationReport)

    def test_filename_stored(self):
        result = classify_entries([], filename="prod.env")
        assert result.filename == "prod.env"

    def test_entries_classified(self):
        entries = [_entry("DB_HOST"), _entry("JWT_SECRET"), _entry("APP_NAME")]
        result = classify_entries(entries)
        cats = [ce.category for ce in result.entries]
        assert Category.DATABASE in cats
        assert Category.AUTH in cats
        assert Category.MISC in cats

    def test_by_category_groups_correctly(self):
        entries = [_entry("DB_HOST"), _entry("DB_PORT"), _entry("LOG_LEVEL")]
        report = classify_entries(entries)
        grouped = report.by_category()
        assert len(grouped[Category.DATABASE]) == 2
        assert len(grouped[Category.LOGGING]) == 1

    def test_category_counts(self):
        entries = [_entry("DB_HOST"), _entry("APP_NAME")]
        report = classify_entries(entries)
        counts = report.category_counts
        assert counts.get("database", 0) == 1
        assert counts.get("misc", 0) == 1

    def test_entries_without_key_are_skipped(self):
        blank = EnvEntry(key=None, value=None, raw="# comment")
        result = classify_entries([blank])
        assert result.entries == []

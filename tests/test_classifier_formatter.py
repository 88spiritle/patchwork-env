"""Tests for patchwork_env.classifier_formatter."""
from __future__ import annotations

import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_classifier import classify_entries, Category
from patchwork_env.classifier_formatter import format_classification, format_classification_summary


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


@pytest.fixture
def sample_report():
    entries = [
        _entry("DB_HOST"),
        _entry("JWT_SECRET"),
        _entry("LOG_LEVEL"),
        _entry("APP_NAME"),
    ]
    return classify_entries(entries, filename="staging.env")


class TestFormatClassification:
    def test_contains_filename(self, sample_report):
        out = format_classification(sample_report)
        assert "staging.env" in out

    def test_shows_database_category(self, sample_report):
        out = format_classification(sample_report)
        assert "DATABASE" in out

    def test_shows_auth_category(self, sample_report):
        out = format_classification(sample_report)
        assert "AUTH" in out

    def test_shows_key_under_category(self, sample_report):
        out = format_classification(sample_report)
        assert "DB_HOST" in out
        assert "JWT_SECRET" in out

    def test_empty_categories_omitted(self, sample_report):
        out = format_classification(sample_report)
        # STORAGE has no entries, should not appear
        assert "STORAGE" not in out

    def test_returns_string(self, sample_report):
        out = format_classification(sample_report)
        assert isinstance(out, str)


class TestFormatClassificationSummary:
    def test_contains_filename(self, sample_report):
        out = format_classification_summary(sample_report)
        assert "staging.env" in out

    def test_shows_total_count(self, sample_report):
        out = format_classification_summary(sample_report)
        assert "4" in out

    def test_shows_category_breakdown(self, sample_report):
        out = format_classification_summary(sample_report)
        assert "database" in out
        assert "auth" in out

    def test_fallback_filename(self):
        from patchwork_env.env_classifier import ClassificationReport
        report = ClassificationReport(filename="")
        out = format_classification_summary(report)
        assert "env" in out

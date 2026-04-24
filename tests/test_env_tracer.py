"""Tests for patchwork_env.env_tracer."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_tracer import TraceRecord, TraceReport, trace_entries


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# TraceRecord
# ---------------------------------------------------------------------------

class TestTraceRecord:
    def test_is_unique_single_source(self):
        r = TraceRecord(key="FOO", sources=["a.env"], values=["1"])
        assert r.is_unique is True

    def test_is_unique_multiple_sources(self):
        r = TraceRecord(key="FOO", sources=["a.env", "b.env"], values=["1", "1"])
        assert r.is_unique is False

    def test_is_conflicted_same_values(self):
        r = TraceRecord(key="FOO", sources=["a.env", "b.env"], values=["1", "1"])
        assert r.is_conflicted is False

    def test_is_conflicted_different_values(self):
        r = TraceRecord(key="FOO", sources=["a.env", "b.env"], values=["1", "2"])
        assert r.is_conflicted is True


# ---------------------------------------------------------------------------
# trace_entries
# ---------------------------------------------------------------------------

@pytest.fixture()
def sources():
    return {
        "base.env": [
            _entry("DB_HOST", "localhost"),
            _entry("DB_PORT", "5432"),
            _entry("APP_ENV", "development"),
        ],
        "prod.env": [
            _entry("DB_HOST", "db.prod.example.com"),
            _entry("APP_ENV", "production"),
            _entry("SECRET_KEY", "s3cr3t"),
        ],
    }


def test_report_file_names_set(sources):
    report = trace_entries(sources)
    assert report.file_names == ["base.env", "prod.env"]


def test_unique_key_detected(sources):
    report = trace_entries(sources)
    assert "DB_PORT" in report.unique_keys


def test_conflicted_key_detected(sources):
    report = trace_entries(sources)
    assert "DB_HOST" in report.conflicted_keys
    assert "APP_ENV" in report.conflicted_keys


def test_non_conflicted_shared_key_not_in_conflicted(sources):
    """A key present in two files with the same value is NOT conflicted."""
    sources_same = {
        "a.env": [_entry("PORT", "8080")],
        "b.env": [_entry("PORT", "8080")],
    }
    report = trace_entries(sources_same)
    assert "PORT" not in report.conflicted_keys


def test_get_returns_record(sources):
    report = trace_entries(sources)
    record = report.get("DB_HOST")
    assert record is not None
    assert record.key == "DB_HOST"


def test_get_returns_none_for_missing(sources):
    report = trace_entries(sources)
    assert report.get("NONEXISTENT") is None


def test_keys_are_uppercased():
    sources = {"a.env": [_entry("db_host", "localhost")]}
    report = trace_entries(sources)
    assert "DB_HOST" in report.records


def test_blank_key_entries_skipped():
    sources = {"a.env": [EnvEntry(key=None, value=None, raw="# comment")]}
    report = trace_entries(sources)
    assert len(report.records) == 0


def test_sources_and_values_aligned(sources):
    report = trace_entries(sources)
    record = report.get("DB_HOST")
    assert len(record.sources) == len(record.values) == 2

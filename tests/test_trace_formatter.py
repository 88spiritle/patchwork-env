"""Tests for patchwork_env.trace_formatter."""
from __future__ import annotations

from patchwork_env.parser import EnvEntry
from patchwork_env.env_tracer import trace_entries
from patchwork_env.trace_formatter import (
    format_trace_record,
    format_trace_report,
    format_trace_summary,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_report():
    sources = {
        "base.env": [
            _entry("DB_HOST", "localhost"),
            _entry("PORT", "5432"),
        ],
        "prod.env": [
            _entry("DB_HOST", "db.prod.example.com"),
            _entry("SECRET", "xyz"),
        ],
    }
    return trace_entries(sources)


# ---------------------------------------------------------------------------
# format_trace_record
# ---------------------------------------------------------------------------

def test_record_contains_key():
    from patchwork_env.env_tracer import TraceRecord
    r = TraceRecord(key="FOO", sources=["a.env"], values=["bar"])
    output = format_trace_record(r)
    assert "FOO" in output


def test_record_shows_source_filename():
    from patchwork_env.env_tracer import TraceRecord
    r = TraceRecord(key="FOO", sources=["a.env"], values=["bar"])
    output = format_trace_record(r)
    assert "a.env" in output


def test_record_shows_conflict_label():
    from patchwork_env.env_tracer import TraceRecord
    r = TraceRecord(key="DB", sources=["a.env", "b.env"], values=["1", "2"])
    output = format_trace_record(r)
    assert "CONFLICT" in output


def test_record_shows_ok_when_no_conflict():
    from patchwork_env.env_tracer import TraceRecord
    r = TraceRecord(key="X", sources=["a.env"], values=["1"])
    output = format_trace_record(r)
    assert "ok" in output


# ---------------------------------------------------------------------------
# format_trace_report
# ---------------------------------------------------------------------------

def test_report_contains_header():
    report = _make_report()
    output = format_trace_report(report)
    assert "Trace Report" in output


def test_report_lists_filenames():
    report = _make_report()
    output = format_trace_report(report)
    assert "base.env" in output
    assert "prod.env" in output


def test_report_shows_all_keys():
    report = _make_report()
    output = format_trace_report(report)
    assert "DB_HOST" in output
    assert "PORT" in output
    assert "SECRET" in output


# ---------------------------------------------------------------------------
# format_trace_summary
# ---------------------------------------------------------------------------

def test_summary_mentions_total_keys():
    report = _make_report()
    summary = format_trace_summary(report)
    assert "3" in summary  # 3 distinct keys


def test_summary_mentions_file_count():
    report = _make_report()
    summary = format_trace_summary(report)
    assert "2" in summary


def test_summary_mentions_conflicted():
    report = _make_report()
    summary = format_trace_summary(report)
    assert "conflicted" in summary

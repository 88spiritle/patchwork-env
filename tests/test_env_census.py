"""Tests for env_census.py and census_formatter.py."""
from __future__ import annotations

import pytest

from patchwork_env.env_census import CensusRow, CensusReport, build_census
from patchwork_env.census_formatter import format_census, format_census_summary
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str, source: str = "base.env") -> EnvEntry:
    e = EnvEntry()
    e.key = key
    e.value = value
    e.source = source
    return e


# ---------------------------------------------------------------------------
# CensusRow
# ---------------------------------------------------------------------------

class TestCensusRow:
    def test_consistent_single_value(self):
        row = CensusRow(key="FOO", occurrences=2, unique_values=["bar"], sources=["a", "b"])
        assert row.is_consistent is True

    def test_inconsistent_multiple_values(self):
        row = CensusRow(key="FOO", occurrences=2, unique_values=["bar", "baz"], sources=["a", "b"])
        assert row.is_consistent is False

    def test_zero_unique_values_is_consistent(self):
        row = CensusRow(key="FOO", occurrences=0, unique_values=[], sources=[])
        assert row.is_consistent is True


# ---------------------------------------------------------------------------
# CensusReport
# ---------------------------------------------------------------------------

class TestCensusReport:
    def _make_report(self) -> CensusReport:
        rows = [
            CensusRow("DB_HOST", 2, ["localhost"], ["a.env", "b.env"]),
            CensusRow("DB_PORT", 2, ["5432", "3306"], ["a.env", "b.env"]),
            CensusRow("SECRET", 1, ["abc"], ["a.env"]),
        ]
        return CensusReport(filenames=["a.env", "b.env"], rows=rows)

    def test_total_keys(self):
        assert self._make_report().total_keys == 3

    def test_consistent_keys(self):
        report = self._make_report()
        assert len(report.consistent_keys) == 2

    def test_inconsistent_keys(self):
        report = self._make_report()
        assert len(report.inconsistent_keys) == 1
        assert report.inconsistent_keys[0].key == "DB_PORT"


# ---------------------------------------------------------------------------
# build_census
# ---------------------------------------------------------------------------

@pytest.fixture
def env_a():
    return [
        _entry("DB_HOST", "localhost", "a.env"),
        _entry("DB_PORT", "5432", "a.env"),
        _entry("SECRET", "abc", "a.env"),
    ]


@pytest.fixture
def env_b():
    return [
        _entry("DB_HOST", "localhost", "b.env"),
        _entry("DB_PORT", "3306", "b.env"),
        _entry("API_KEY", "xyz", "b.env"),
    ]


def test_build_census_filenames(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    assert report.filenames == ["a.env", "b.env"]


def test_build_census_total_keys(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    assert report.total_keys == 4  # DB_HOST, DB_PORT, SECRET, API_KEY


def test_build_census_consistent_key(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    db_host = next(r for r in report.rows if r.key == "DB_HOST")
    assert db_host.is_consistent is True
    assert db_host.occurrences == 2


def test_build_census_inconsistent_key(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    db_port = next(r for r in report.rows if r.key == "DB_PORT")
    assert db_port.is_consistent is False
    assert set(db_port.unique_values) == {"5432", "3306"}


def test_build_census_single_source_key(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    secret = next(r for r in report.rows if r.key == "SECRET")
    assert secret.occurrences == 1
    assert secret.sources == ["a.env"]


def test_build_census_rows_sorted(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    keys = [r.key for r in report.rows]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_census_contains_header(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    text = format_census(report)
    assert "Census Report" in text


def test_format_census_shows_key(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    text = format_census(report)
    assert "DB_HOST" in text


def test_format_census_shows_totals(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    text = format_census(report)
    assert "total keys" in text


def test_format_census_summary_consistent(env_a):
    report = build_census([("a.env", env_a)])
    summary = format_census_summary(report)
    assert "consistent" in summary


def test_format_census_summary_inconsistent(env_a, env_b):
    report = build_census([("a.env", env_a), ("b.env", env_b)])
    summary = format_census_summary(report)
    assert "DB_PORT" in summary

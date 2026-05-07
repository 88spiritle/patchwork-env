"""Tests for env_comparer and comparer_formatter."""
import pytest
from patchwork_env.env_comparer import (
    KeyComparison,
    CrossEnvReport,
    compare_across_envs,
)
from patchwork_env.comparer_formatter import (
    format_cross_env_report,
    format_cross_env_summary,
)


# ---------------------------------------------------------------------------
# KeyComparison
# ---------------------------------------------------------------------------

class TestKeyComparison:
    def test_consistent_when_all_same(self):
        cmp = KeyComparison(key="PORT", values={"dev": "8080", "prod": "8080"})
        assert cmp.is_consistent is True

    def test_inconsistent_when_values_differ(self):
        cmp = KeyComparison(key="PORT", values={"dev": "8080", "prod": "443"})
        assert cmp.is_consistent is False

    def test_missing_in_reports_absent_envs(self):
        cmp = KeyComparison(key="SECRET", values={"dev": "abc", "prod": None})
        assert "prod" in cmp.missing_in
        assert "dev" not in cmp.missing_in

    def test_unique_values_excludes_none(self):
        cmp = KeyComparison(key="X", values={"a": "1", "b": None, "c": "1"})
        assert cmp.unique_values == ["1"]

    def test_repr_contains_key(self):
        cmp = KeyComparison(key="FOO", values={"dev": "bar"})
        assert "FOO" in repr(cmp)


# ---------------------------------------------------------------------------
# compare_across_envs
# ---------------------------------------------------------------------------

@pytest.fixture
def env_maps():
    return {
        "dev":  {"PORT": "8080", "DEBUG": "true",  "SECRET": "dev-secret"},
        "prod": {"PORT": "443",  "DEBUG": "false", "SECRET": "prod-secret"},
        "test": {"PORT": "8080", "DEBUG": "true"},
    }


def test_report_env_names_set(env_maps):
    report = compare_across_envs(env_maps)
    assert set(report.env_names) == {"dev", "prod", "test"}


def test_all_keys_discovered(env_maps):
    report = compare_across_envs(env_maps)
    keys = [c.key for c in report.comparisons]
    assert "PORT" in keys
    assert "DEBUG" in keys
    assert "SECRET" in keys


def test_explicit_keys_respected(env_maps):
    report = compare_across_envs(env_maps, keys=["PORT"])
    assert len(report.comparisons) == 1
    assert report.comparisons[0].key == "PORT"


def test_missing_key_shows_none(env_maps):
    report = compare_across_envs(env_maps, keys=["SECRET"])
    cmp = report.comparisons[0]
    assert cmp.values["test"] is None


def test_inconsistent_keys_detected(env_maps):
    report = compare_across_envs(env_maps)
    inconsistent_names = {c.key for c in report.inconsistent_keys}
    assert "PORT" not in inconsistent_names  # dev & test agree; prod differs — actually differs
    assert "SECRET" in inconsistent_names


def test_consistent_keys_detected(env_maps):
    # PORT: dev=8080, prod=443, test=8080  -> inconsistent
    # DEBUG: dev=true, prod=false, test=true -> inconsistent
    # SECRET: dev!=prod, test missing -> inconsistent
    # Use a simple case
    maps = {"a": {"X": "1"}, "b": {"X": "1"}}
    report = compare_across_envs(maps, keys=["X"])
    assert len(report.consistent_keys) == 1


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_report_contains_env_names(env_maps):
    report = compare_across_envs(env_maps, keys=["PORT"])
    output = format_cross_env_report(report)
    assert "dev" in output
    assert "prod" in output


def test_format_report_shows_key(env_maps):
    report = compare_across_envs(env_maps, keys=["PORT"])
    output = format_cross_env_report(report)
    assert "PORT" in output


def test_format_summary_contains_count(env_maps):
    report = compare_across_envs(env_maps)
    summary = format_cross_env_summary(report)
    assert "3" in summary  # 3 keys total


def test_format_summary_empty():
    report = CrossEnvReport(key="*", env_names=["a", "b"], comparisons=[])
    output = format_cross_env_report(report)
    assert "no keys" in output

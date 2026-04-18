"""Tests for env_comparator and comparator_formatter."""
import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_comparator import compare_envs, ComparisonReport
from patchwork_env.comparator_formatter import format_comparison, format_comparison_summary


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


@pytest.fixture
def entries_a():
    return [_entry("HOST", "localhost"), _entry("PORT", "5432"), _entry("DEBUG", "true")]


@pytest.fixture
def entries_b():
    return [_entry("HOST", "prod.example.com"), _entry("PORT", "5432"), _entry("SECRET", "abc")]


@pytest.fixture
def report(entries_a, entries_b):
    return compare_envs(entries_a, entries_b, file_a=".env.dev", file_b=".env.prod")


def test_file_names_set(report):
    assert report.file_a == ".env.dev"
    assert report.file_b == ".env.prod"


def test_common_keys(report):
    assert "HOST" in report.common_keys
    assert "PORT" in report.common_keys


def test_only_in_a(report):
    assert report.only_in_a == ["DEBUG"]


def test_only_in_b(report):
    assert report.only_in_b == ["SECRET"]


def test_value_match(report):
    assert "PORT" in report.value_matches


def test_value_mismatch(report):
    assert "HOST" in report.value_mismatches


def test_similarity_score_between_0_and_1(report):
    assert 0.0 <= report.similarity_score <= 1.0


def test_empty_envs_score_is_1():
    r = compare_envs([], [])
    assert r.similarity_score == 1.0


def test_identical_envs_score_is_1():
    entries = [_entry("A", "1"), _entry("B", "2")]
    r = compare_envs(entries, entries)
    assert r.similarity_score == 1.0


def test_format_comparison_contains_filenames(report):
    out = format_comparison(report)
    assert ".env.dev" in out
    assert ".env.prod" in out


def test_format_comparison_shows_mismatches(report):
    out = format_comparison(report)
    assert "HOST" in out


def test_format_summary_contains_score(report):
    out = format_comparison_summary(report)
    assert str(report.similarity_score) in out

"""Tests for patchwork_env.formatter module."""

import pytest

from patchwork_env.differ import diff_env_files
from patchwork_env.formatter import format_diff, format_summary
from patchwork_env.parser import EnvFile, EnvEntry


def make_env_file(pairs: dict, path: str = "test.env") -> EnvFile:
    entries = [
        EnvEntry(key=k, raw_value=v, comment=None)
        for k, v in pairs.items()
    ]
    return EnvFile(entries=entries, path=path)


@pytest.fixture
def sample_diff():
    base = make_env_file({"A": "1", "B": "old", "C": "same"}, path=".env.base")
    target = make_env_file({"B": "new", "C": "same", "D": "4"}, path=".env.target")
    return diff_env_files(base, target)


def test_format_diff_contains_header(sample_diff):
    output = format_diff(sample_diff, color=False)
    assert "--- .env.base" in output
    assert "+++ .env.target" in output


def test_format_diff_shows_added(sample_diff):
    output = format_diff(sample_diff, color=False)
    assert "+ D=" in output


def test_format_diff_shows_removed(sample_diff):
    output = format_diff(sample_diff, color=False)
    assert "- A=" in output


def test_format_diff_shows_modified(sample_diff):
    output = format_diff(sample_diff, color=False)
    assert "~ B:" in output
    assert "'old'" in output
    assert "'new'" in output


def test_format_diff_hides_unchanged_by_default(sample_diff):
    output = format_diff(sample_diff, color=False, show_unchanged=False)
    assert "  C=" not in output


def test_format_diff_shows_unchanged_when_requested(sample_diff):
    output = format_diff(sample_diff, color=False, show_unchanged=True)
    assert "C=" in output


def test_format_diff_no_changes_message():
    env = make_env_file({"X": "1"}, path="a")
    diff = diff_env_files(env, env)
    output = format_diff(diff, color=False)
    assert "(no differences)" in output


def test_format_summary_with_changes(sample_diff):
    summary = format_summary(sample_diff)
    assert "added" in summary
    assert "removed" in summary
    assert "modified" in summary


def test_format_summary_identical():
    env = make_env_file({"X": "1"}, path="a")
    diff = diff_env_files(env, env)
    summary = format_summary(diff)
    assert "identical" in summary

"""Tests for env_differ_summary and diff_summary_formatter."""

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.differ import EnvDiff
from patchwork_env.env_differ_summary import EnvDiffSummary, summarise_diffs
from patchwork_env.diff_summary_formatter import (
    format_diff_summary,
    format_diff_summary_oneliner,
)


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


def _make_env(pairs: dict[str, str], name: str = "test.env"):
    """Build a minimal list of EnvEntry objects."""
    return [_entry(k, v) for k, v in pairs.items()]


@pytest.fixture()
def diff_a() -> EnvDiff:
    base = _make_env({"A": "1", "B": "2", "C": "3"})
    target = _make_env({"A": "1", "B": "changed", "D": "4"})
    return EnvDiff.compute(base, target, base_name="base.env", target_name="prod.env")


@pytest.fixture()
def diff_b() -> EnvDiff:
    base = _make_env({"X": "10", "Y": "20"})
    target = _make_env({"X": "10", "Y": "20"})
    return EnvDiff.compute(base, target, base_name="staging.env", target_name="qa.env")


# --- EnvDiffSummary unit tests ---

def test_empty_summary_zero_totals():
    s = EnvDiffSummary()
    assert s.total_changes == 0
    assert s.total_keys == 0
    assert s.change_ratio == 0.0


def test_summarise_single_diff(diff_a):
    s = summarise_diffs([diff_a])
    assert s.total_added == 1       # D added
    assert s.total_removed == 1     # C removed
    assert s.total_modified == 1    # B modified
    assert s.total_unchanged == 1   # A unchanged


def test_summarise_multiple_diffs(diff_a, diff_b):
    s = summarise_diffs([diff_a, diff_b])
    assert len(s.names) == 2
    assert s.total_unchanged == 3   # A (diff_a) + X + Y (diff_b)


def test_names_contain_arrow(diff_a):
    s = summarise_diffs([diff_a])
    assert "→" in s.names[0]
    assert "base.env" in s.names[0]
    assert "prod.env" in s.names[0]


def test_change_ratio_nonzero(diff_a):
    s = summarise_diffs([diff_a])
    assert 0.0 < s.change_ratio <= 1.0


def test_change_ratio_zero_when_no_changes(diff_b):
    s = summarise_diffs([diff_b])
    assert s.change_ratio == 0.0


# --- Formatter tests ---

def test_format_diff_summary_contains_header(diff_a):
    s = summarise_diffs([diff_a])
    output = format_diff_summary(s)
    assert "Diff Summary" in output


def test_format_diff_summary_shows_counts(diff_a):
    s = summarise_diffs([diff_a])
    output = format_diff_summary(s)
    assert "Added" in output
    assert "Removed" in output
    assert "Modified" in output


def test_format_diff_summary_empty():
    s = EnvDiffSummary()
    output = format_diff_summary(s)
    assert "No diffs" in output


def test_format_oneliner_contains_all_fields(diff_a):
    s = summarise_diffs([diff_a])
    line = format_diff_summary_oneliner(s)
    for field in ("pairs=", "added=", "removed=", "modified=", "unchanged="):
        assert field in line

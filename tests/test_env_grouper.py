"""Tests for env_grouper module."""
import pytest
from patchwork_env.parser import EnvEntry
from patchwork_env.env_grouper import (
    EntryGroup,
    group_by_prefix,
    group_by_label,
    flat_sorted_groups,
)


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, raw_value=value, comment=None, original_line=f"{key}={value}")


@pytest.fixture
def entries():
    return [
        _entry("DB_HOST", "localhost"),
        _entry("DB_PORT", "5432"),
        _entry("APP_ENV", "production"),
        _entry("APP_DEBUG", "false"),
        _entry("SECRET", "abc123"),
    ]


def test_group_by_prefix_creates_correct_groups(entries):
    groups = group_by_prefix(entries)
    assert "DB" in groups
    assert "APP" in groups
    assert "SECRET" in groups


def test_group_by_prefix_entry_counts(entries):
    groups = group_by_prefix(entries)
    assert len(groups["DB"].entries) == 2
    assert len(groups["APP"].entries) == 2
    assert len(groups["SECRET"].entries) == 1


def test_group_by_prefix_label_matches_key(entries):
    groups = group_by_prefix(entries)
    assert groups["DB"].label == "DB"


def test_group_by_label_uses_mapping(entries):
    mapping = {"DB_HOST": "database", "DB_PORT": "database", "APP_ENV": "app"}
    groups = group_by_label(entries, mapping)
    assert "database" in groups
    assert "app" in groups
    assert "other" in groups


def test_group_by_label_unmapped_goes_to_other(entries):
    groups = group_by_label(entries, {})
    assert "other" in groups
    assert len(groups["other"].entries) == len(entries)


def test_flat_sorted_groups_returns_alphabetical(entries):
    groups = group_by_prefix(entries)
    sorted_groups = flat_sorted_groups(groups)
    labels = [g.label for g in sorted_groups]
    assert labels == sorted(labels)


def test_entry_group_repr():
    g = EntryGroup(label="DB", entries=[_entry("DB_HOST")])
    assert "DB" in repr(g)
    assert "count=1" in repr(g)


def test_no_key_entries_are_skipped():
    entries = [EnvEntry(key=None, raw_value=None, comment="# comment", original_line="# comment")]
    groups = group_by_prefix(entries)
    assert len(groups) == 0

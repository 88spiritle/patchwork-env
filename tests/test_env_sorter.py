"""Tests for patchwork_env.env_sorter."""

from __future__ import annotations

import pytest

from patchwork_env.env_sorter import SortMode, group_by_prefix, sort_entries
from patchwork_env.parser import EnvEntry


def _entry(key: str, value: str = "v") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw_line=f"{key}={value}")


@pytest.fixture()
def unsorted_entries():
    return [
        _entry("ZEBRA"),
        _entry("APP_HOST"),
        _entry("DB_PORT"),
        _entry("APP_PORT"),
        _entry("DB_HOST"),
        _entry("ALPHA"),
    ]


def test_sort_alphabetical(unsorted_entries):
    result = sort_entries(unsorted_entries, mode=SortMode.ALPHABETICAL)
    keys = [e.key for e in result]
    assert keys == sorted(keys)


def test_sort_reverse(unsorted_entries):
    result = sort_entries(unsorted_entries, mode=SortMode.REVERSE)
    keys = [e.key for e in result]
    assert keys == sorted(keys, reverse=True)


def test_sort_preserve_returns_same_order(unsorted_entries):
    result = sort_entries(unsorted_entries, mode=SortMode.PRESERVE)
    assert [e.key for e in result] == [e.key for e in unsorted_entries]


def test_sort_does_not_mutate_original(unsorted_entries):
    original_order = [e.key for e in unsorted_entries]
    sort_entries(unsorted_entries, mode=SortMode.ALPHABETICAL)
    assert [e.key for e in unsorted_entries] == original_order


def test_sort_by_prefix_respects_order(unsorted_entries):
    result = sort_entries(
        unsorted_entries,
        mode=SortMode.BY_PREFIX,
        custom_order=["DB", "APP"],
    )
    keys = [e.key for e in result]
    db_indices = [i for i, k in enumerate(keys) if k.startswith("DB")]
    app_indices = [i for i, k in enumerate(keys) if k.startswith("APP")]
    assert max(db_indices) < min(app_indices)


def test_sort_by_prefix_unknown_prefixes_sort_last(unsorted_entries):
    result = sort_entries(
        unsorted_entries,
        mode=SortMode.BY_PREFIX,
        custom_order=["APP", "DB"],
    )
    keys = [e.key for e in result]
    # ALPHA and ZEBRA have no underscore → prefix == key → not in order list
    for unknown in ("ALPHA", "ZEBRA"):
        assert keys.index(unknown) > keys.index("APP_HOST")


def test_group_by_prefix_correct_keys(unsorted_entries):
    groups = group_by_prefix(unsorted_entries)
    assert set(groups.keys()) == {"ZEBRA", "APP", "DB", "ALPHA"}


def test_group_by_prefix_member_counts(unsorted_entries):
    groups = group_by_prefix(unsorted_entries)
    assert len(groups["APP"]) == 2
    assert len(groups["DB"]) == 2


def test_sort_unknown_mode_raises():
    with pytest.raises(ValueError):
        sort_entries([], mode="bogus")  # type: ignore[arg-type]

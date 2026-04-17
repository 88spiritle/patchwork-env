"""Tests for patchwork_env.env_duplicator."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_duplicator import find_duplicates, DuplicateGroup, DuplicateReport


def _entry(key: str, value: str = "val") -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}")


@pytest.fixture()
def entries_with_duplicates():
    return [
        _entry("HOST", "localhost"),
        _entry("PORT", "5432"),
        _entry("HOST", "remotehost"),
        _entry("DEBUG", "true"),
        _entry("PORT", "6543"),
        _entry("PORT", "9999"),
    ]


@pytest.fixture()
def unique_entries():
    return [_entry("A"), _entry("B"), _entry("C")]


def test_no_duplicates_returns_empty_report(unique_entries):
    report = find_duplicates(unique_entries, filename=".env")
    assert not report.has_duplicates
    assert report.groups == []


def test_has_duplicates_true_when_duplicates_present(entries_with_duplicates):
    report = find_duplicates(entries_with_duplicates, filename=".env")
    assert report.has_duplicates


def test_duplicate_keys_listed(entries_with_duplicates):
    report = find_duplicates(entries_with_duplicates, filename=".env")
    assert set(report.duplicate_keys) == {"HOST", "PORT"}


def test_groups_sorted_alphabetically(entries_with_duplicates):
    report = find_duplicates(entries_with_duplicates, filename=".env")
    assert report.duplicate_keys == sorted(report.duplicate_keys)


def test_occurrences_count_correct(entries_with_duplicates):
    report = find_duplicates(entries_with_duplicates, filename=".env")
    port_group = next(g for g in report.groups if g.key == "PORT")
    assert len(port_group.occurrences) == 3


def test_occurrences_values_preserved(entries_with_duplicates):
    report = find_duplicates(entries_with_duplicates, filename=".env")
    host_group = next(g for g in report.groups if g.key == "HOST")
    values = [e.value for e in host_group.occurrences]
    assert "localhost" in values
    assert "remotehost" in values


def test_filename_stored_in_report(entries_with_duplicates):
    report = find_duplicates(entries_with_duplicates, filename="prod.env")
    assert report.filename == "prod.env"


def test_empty_entries_returns_empty_report():
    report = find_duplicates([], filename=".env")
    assert not report.has_duplicates


def test_single_entry_no_duplicate():
    report = find_duplicates([_entry("ONLY")], filename=".env")
    assert not report.has_duplicates

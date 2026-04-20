"""Tests for archive_formatter module."""

from __future__ import annotations

import pytest

from patchwork_env.env_archiver import Archive, ArchiveEntry
from patchwork_env.archive_formatter import format_archive, format_archive_entry, format_archive_summary
from patchwork_env.snapshot import Snapshot
from patchwork_env.parser import EnvEntry


def _make_snapshot(filename: str = "staging.env", keys: list[str] | None = None) -> Snapshot:
    keys = keys or ["APP", "SECRET"]
    entries = [EnvEntry(key=k, value="x", raw=f"{k}=x", comment="", line_number=i + 1) for i, k in enumerate(keys)]
    return Snapshot(filename=filename, entries=entries)


@pytest.fixture
def archive() -> Archive:
    a = Archive(name="staging-archive")
    a.add(_make_snapshot(), label="v1.0")
    a.add(_make_snapshot(keys=["DB", "CACHE", "HOST"]), label="v1.1")
    return a


def test_format_archive_entry_contains_label():
    snap = _make_snapshot()
    entry = ArchiveEntry(timestamp="2024-06-01T12:00:00+00:00", label="release", snapshot=snap)
    output = format_archive_entry(entry)
    assert "release" in output


def test_format_archive_entry_contains_filename():
    snap = _make_snapshot(filename="prod.env")
    entry = ArchiveEntry(timestamp="2024-06-01T12:00:00+00:00", label="x", snapshot=snap)
    output = format_archive_entry(entry)
    assert "prod.env" in output


def test_format_archive_entry_shows_key_count():
    snap = _make_snapshot(keys=["A", "B", "C"])
    entry = ArchiveEntry(timestamp="2024-06-01T12:00:00+00:00", label="x", snapshot=snap)
    output = format_archive_entry(entry)
    assert "3" in output


def test_format_archive_contains_archive_name(archive: Archive):
    output = format_archive(archive)
    assert "staging-archive" in output


def test_format_archive_lists_all_entries(archive: Archive):
    output = format_archive(archive)
    assert "v1.0" in output
    assert "v1.1" in output


def test_format_archive_empty_message():
    empty = Archive(name="empty-archive")
    output = format_archive(empty)
    assert "empty" in output.lower()


def test_format_archive_summary_contains_name(archive: Archive):
    output = format_archive_summary(archive)
    assert "staging-archive" in output


def test_format_archive_summary_shows_count(archive: Archive):
    output = format_archive_summary(archive)
    assert "2" in output


def test_format_archive_summary_shows_latest_label(archive: Archive):
    output = format_archive_summary(archive)
    assert "v1.1" in output


def test_format_archive_summary_empty_archive():
    empty = Archive(name="empty")
    output = format_archive_summary(empty)
    assert "no snapshots" in output.lower()

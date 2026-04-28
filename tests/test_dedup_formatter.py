"""Tests for patchwork_env.dedup_formatter."""
from __future__ import annotations

import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_deduplicator import deduplicate
from patchwork_env.dedup_formatter import format_dedup_result, format_dedup_summary


def _entry(key: str, value: str, line: int = 1) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw=f"{key}={value}", line_number=line)


@pytest.fixture()
def clean_result():
    entries = [_entry("HOST", "localhost", 1), _entry("PORT", "5432", 2)]
    return deduplicate(entries, filename="clean.env")


@pytest.fixture()
def duped_result():
    entries = [
        _entry("HOST", "localhost", 1),
        _entry("HOST", "prod.example.com", 3),
        _entry("DB", "mydb", 4),
    ]
    return deduplicate(entries, filename="duped.env")


# --- format_dedup_result ---

def test_format_result_contains_filename(duped_result):
    out = format_dedup_result(duped_result)
    assert "duped.env" in out


def test_format_result_shows_affected_key(duped_result):
    out = format_dedup_result(duped_result)
    assert "HOST" in out


def test_format_result_clean_message(clean_result):
    out = format_dedup_result(clean_result)
    assert "No duplicate" in out


def test_format_result_shows_removed_count(duped_result):
    out = format_dedup_result(duped_result)
    assert "1" in out  # 1 duplicate removed for HOST


# --- format_dedup_summary ---

def test_summary_clean_shows_clean(clean_result):
    out = format_dedup_summary(clean_result)
    assert "clean" in out


def test_summary_duped_shows_removed(duped_result):
    out = format_dedup_summary(duped_result)
    assert "removed" in out


def test_summary_contains_filename(duped_result):
    out = format_dedup_summary(duped_result)
    assert "duped.env" in out


def test_summary_clean_contains_filename(clean_result):
    out = format_dedup_summary(clean_result)
    assert "clean.env" in out

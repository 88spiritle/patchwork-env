"""Tests for patchwork_env.env_dependency."""
from __future__ import annotations

import pytest
from patchwork_env.env_dependency import (
    _refs_in_value,
    analyse_dependencies,
    DependencyEdge,
    DependencyReport,
)


# ------------------------------------------------------------------ helpers

class _Entry:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


def _entry(key: str, value: str = "") -> _Entry:
    return _Entry(key, value)


# ------------------------------------------------------------------ _refs_in_value

def test_no_refs_returns_empty():
    assert _refs_in_value("plain_value") == []


def test_brace_syntax_detected():
    assert _refs_in_value("${HOST}") == ["HOST"]


def test_dollar_syntax_detected():
    assert _refs_in_value("$PORT") == ["PORT"]


def test_multiple_refs_returned():
    refs = _refs_in_value("${PROTO}://${HOST}:$PORT")
    assert refs == ["PROTO", "HOST", "PORT"]


def test_lowercase_not_matched():
    assert _refs_in_value("${not_a_key}") == []


# ------------------------------------------------------------------ analyse_dependencies

def test_no_deps_returns_empty_edges():
    entries = [_entry("FOO", "bar"), _entry("BAZ", "qux")]
    report = analyse_dependencies(entries, filename="test.env")
    assert report.edges == []


def test_defined_dependency_detected():
    entries = [
        _entry("HOST", "localhost"),
        _entry("URL", "http://${HOST}/path"),
    ]
    report = analyse_dependencies(entries)
    assert len(report.edges) == 1
    edge = report.edges[0]
    assert edge.source_key == "URL"
    assert edge.target_key == "HOST"
    assert edge.defined is True


def test_undefined_dependency_flagged():
    entries = [_entry("URL", "http://${MISSING_HOST}/path")]
    report = analyse_dependencies(entries)
    assert len(report.edges) == 1
    assert report.edges[0].defined is False


def test_has_missing_true_when_undefined():
    entries = [_entry("URL", "$GHOST")]
    report = analyse_dependencies(entries)
    assert report.has_missing is True


def test_has_missing_false_when_all_defined():
    entries = [
        _entry("BASE", "http://localhost"),
        _entry("URL", "${BASE}/api"),
    ]
    report = analyse_dependencies(entries)
    assert report.has_missing is False


def test_dependency_map_groups_targets():
    entries = [
        _entry("A", "1"),
        _entry("B", "2"),
        _entry("C", "${A}/${B}"),
    ]
    report = analyse_dependencies(entries)
    dep_map = report.dependency_map()
    assert dep_map["C"] == {"A", "B"}


def test_filename_stored():
    report = analyse_dependencies([], filename="prod.env")
    assert report.filename == "prod.env"


def test_blank_key_entries_skipped():
    entries = [_Entry("", "${GHOST}"), _entry("REAL", "val")]
    report = analyse_dependencies(entries)
    assert report.edges == []

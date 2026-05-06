"""Tests for patchwork_env.dependency_formatter."""
from __future__ import annotations

import pytest
from patchwork_env.env_dependency import DependencyEdge, DependencyReport
from patchwork_env.dependency_formatter import (
    format_dependency_report,
    format_dependency_summary,
)


# ------------------------------------------------------------------ helpers

def _report(
    filename: str = "test.env",
    edges: list[DependencyEdge] | None = None,
) -> DependencyReport:
    r = DependencyReport(filename=filename)
    r.edges = edges or []
    return r


# ------------------------------------------------------------------ format_dependency_report

def test_report_contains_filename():
    output = format_dependency_report(_report("staging.env"))
    assert "staging.env" in output


def test_report_no_edges_shows_clean_message():
    output = format_dependency_report(_report())
    assert "No inter-key dependencies" in output


def test_report_shows_defined_edge():
    edge = DependencyEdge(source_key="URL", target_key="HOST", defined=True)
    output = format_dependency_report(_report(edges=[edge]))
    assert "URL" in output
    assert "HOST" in output


def test_report_shows_undefined_edge():
    edge = DependencyEdge(source_key="URL", target_key="MISSING", defined=False)
    output = format_dependency_report(_report(edges=[edge]))
    assert "MISSING" in output
    assert "UNDEFINED" in output


def test_report_missing_section_absent_when_all_defined():
    edge = DependencyEdge(source_key="URL", target_key="HOST", defined=True)
    output = format_dependency_report(_report(edges=[edge]))
    assert "Missing references" not in output


# ------------------------------------------------------------------ format_dependency_summary

def test_summary_contains_filename():
    output = format_dependency_summary(_report("prod.env"))
    assert "prod.env" in output


def test_summary_ok_when_no_missing():
    edge = DependencyEdge(source_key="A", target_key="B", defined=True)
    output = format_dependency_summary(_report(edges=[edge]))
    assert "OK" in output


def test_summary_warn_when_missing():
    edge = DependencyEdge(source_key="A", target_key="GHOST", defined=False)
    output = format_dependency_summary(_report(edges=[edge]))
    assert "WARN" in output


def test_summary_shows_edge_count():
    edges = [
        DependencyEdge("A", "B", True),
        DependencyEdge("C", "D", False),
    ]
    output = format_dependency_summary(_report(edges=edges))
    assert "2" in output

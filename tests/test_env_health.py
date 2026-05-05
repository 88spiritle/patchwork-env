"""Tests for env_health.py and health_formatter.py."""
import pytest

from patchwork_env.env_health import HealthReport, build_health_report
from patchwork_env.health_formatter import format_health_report, format_health_summary


# ---------------------------------------------------------------------------
# HealthReport – grade & is_healthy
# ---------------------------------------------------------------------------

class TestHealthReportGrade:
    def test_perfect_grade_a(self):
        r = build_health_report("prod.env")
        assert r.grade == "A"

    def test_warnings_give_a_minus(self):
        r = build_health_report("prod.env", lint_warnings=1)
        assert r.grade == "A-"

    def test_many_warnings_give_b(self):
        r = build_health_report("prod.env", lint_warnings=4)
        assert r.grade == "B"

    def test_placeholder_gives_c(self):
        r = build_health_report("prod.env", placeholders=2)
        assert r.grade == "C"

    def test_duplicate_gives_c(self):
        r = build_health_report("prod.env", duplicates=1)
        assert r.grade == "C"

    def test_error_gives_f(self):
        r = build_health_report("prod.env", lint_errors=1)
        assert r.grade == "F"

    def test_validation_error_gives_f(self):
        r = build_health_report("prod.env", validation_errors=2)
        assert r.grade == "F"


class TestHealthReportIsHealthy:
    def test_healthy_when_no_issues(self):
        r = build_health_report("dev.env")
        assert r.is_healthy is True

    def test_unhealthy_when_errors(self):
        r = build_health_report("dev.env", lint_errors=1)
        assert r.is_healthy is False

    def test_unhealthy_when_placeholders(self):
        r = build_health_report("dev.env", placeholders=1)
        assert r.is_healthy is False

    def test_healthy_despite_warnings(self):
        """Warnings alone do not make a file unhealthy."""
        r = build_health_report("dev.env", lint_warnings=5)
        assert r.is_healthy is True


class TestHealthReportTotals:
    def test_total_errors_sums_lint_and_validation(self):
        r = build_health_report("x.env", lint_errors=2, validation_errors=3)
        assert r.total_errors == 5

    def test_total_warnings_sums_lint_and_validation(self):
        r = build_health_report("x.env", lint_warnings=1, validation_warnings=2)
        assert r.total_warnings == 3


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_report_contains_filename():
    r = build_health_report("staging.env")
    out = format_health_report(r)
    assert "staging.env" in out


def test_format_report_shows_grade():
    r = build_health_report("staging.env", lint_errors=1)
    out = format_health_report(r)
    assert "F" in out


def test_format_report_shows_notes():
    r = build_health_report("staging.env", notes=["Missing SECRET_KEY"])
    out = format_health_report(r)
    assert "Missing SECRET_KEY" in out


def test_format_summary_counts_files():
    reports = [
        build_health_report("a.env"),
        build_health_report("b.env", lint_errors=1),
    ]
    out = format_health_summary(reports)
    assert "2" in out


def test_format_summary_shows_healthy_count():
    reports = [
        build_health_report("a.env"),
        build_health_report("b.env"),
        build_health_report("c.env", lint_errors=1),
    ]
    out = format_health_summary(reports)
    assert "2" in out  # two healthy


def test_format_summary_lists_filenames():
    reports = [build_health_report("prod.env")]
    out = format_health_summary(reports)
    assert "prod.env" in out

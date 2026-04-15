"""Tests for patchwork_env.reporter."""
from patchwork_env.validator import Severity, ValidationIssue, ValidationResult
from patchwork_env.reporter import format_validation_report, format_validation_summary


def _result(*issues):
    return ValidationResult(issues=list(issues))


def _issue(key, msg, sev):
    return ValidationIssue(key, msg, sev)


# ---------------------------------------------------------------------------
# format_validation_report
# ---------------------------------------------------------------------------

def test_report_no_issues():
    report = format_validation_report(_result())
    assert "No issues found" in report


def test_report_contains_filename():
    report = format_validation_report(_result(), filename=".env.production")
    assert ".env.production" in report


def test_report_shows_error():
    r = _result(_issue("DB_PASS", "Duplicate key", Severity.ERROR))
    report = format_validation_report(r)
    assert "ERROR" in report
    assert "DB_PASS" in report
    assert "Duplicate key" in report


def test_report_shows_warning():
    r = _result(_issue("db_host", "UPPER_SNAKE_CASE", Severity.WARNING))
    report = format_validation_report(r)
    assert "WARNING" in report
    assert "db_host" in report


def test_report_summary_counts():
    r = _result(
        _issue("A", "err", Severity.ERROR),
        _issue("B", "err", Severity.ERROR),
        _issue("C", "warn", Severity.WARNING),
    )
    report = format_validation_report(r)
    assert "2 error(s)" in report
    assert "1 warning(s)" in report


# ---------------------------------------------------------------------------
# format_validation_summary
# ---------------------------------------------------------------------------

def test_summary_lists_files():
    results = {
        ".env.base": _result(),
        ".env.prod": _result(_issue("X", "dup", Severity.ERROR)),
    }
    summary = format_validation_summary(results)
    assert ".env.base" in summary
    assert ".env.prod" in summary


def test_summary_ok_status():
    results = {".env.base": _result()}
    summary = format_validation_summary(results)
    assert "[OK]" in summary


def test_summary_fail_status():
    results = {".env.prod": _result(_issue("K", "e", Severity.ERROR))}
    summary = format_validation_summary(results)
    assert "[FAIL]" in summary

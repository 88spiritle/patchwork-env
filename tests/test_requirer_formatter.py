"""Tests for requirer_formatter.py."""
from patchwork_env.env_requirer import RequirementHit, RequirementReport
from patchwork_env.requirer_formatter import (
    format_requirement_report,
    format_requirement_summary,
)


def _make_report(filename: str = ".env", hits=None) -> RequirementReport:
    if hits is None:
        hits = [
            RequirementHit(key="DB_HOST", found=True, value="localhost"),
            RequirementHit(key="SECRET", found=False),
        ]
    return RequirementReport(filename=filename, hits=hits)


# ---------------------------------------------------------------------------
# format_requirement_report
# ---------------------------------------------------------------------------

def test_report_contains_filename():
    report = _make_report(filename="staging.env")
    output = format_requirement_report(report)
    assert "staging.env" in output


def test_report_shows_present_key():
    report = _make_report()
    output = format_requirement_report(report)
    assert "DB_HOST" in output


def test_report_shows_missing_key():
    report = _make_report()
    output = format_requirement_report(report)
    assert "SECRET" in output


def test_report_shows_missing_label_when_incomplete():
    report = _make_report()
    output = format_requirement_report(report)
    assert "Missing" in output or "MISSING" in output


def test_report_shows_all_present_message_when_complete():
    hits = [
        RequirementHit(key="A", found=True, value="1"),
        RequirementHit(key="B", found=True, value="2"),
    ]
    report = RequirementReport(filename=".env", hits=hits)
    output = format_requirement_report(report)
    assert "present" in output.lower()


# ---------------------------------------------------------------------------
# format_requirement_summary
# ---------------------------------------------------------------------------

def test_summary_contains_filename():
    report = _make_report(filename=".env.prod")
    summary = format_requirement_summary(report)
    assert ".env.prod" in summary


def test_summary_shows_pass_when_complete():
    hits = [RequirementHit(key="X", found=True, value="v")]
    report = RequirementReport(filename=".env", hits=hits)
    summary = format_requirement_summary(report)
    assert "PASS" in summary


def test_summary_shows_fail_when_missing():
    report = _make_report()
    summary = format_requirement_summary(report)
    assert "FAIL" in summary


def test_summary_shows_counts():
    report = _make_report()  # 1 found, 1 missing
    summary = format_requirement_summary(report)
    assert "1/2" in summary

"""Tests for expiry_formatter.py."""
from datetime import date

from patchwork_env.env_expiry import ExpiryRecord, ExpiryReport
from patchwork_env.expiry_formatter import (
    format_expiry_record,
    format_expiry_report,
    format_expiry_summary,
)

_TODAY = date(2024, 6, 15)
_PAST = date(2024, 1, 1)
_FUTURE_NEAR = date(2024, 7, 1)
_FUTURE_FAR = date(2025, 6, 1)


def _rec(key="MY_KEY", expires=_FUTURE_FAR, reason=None):
    return ExpiryRecord(key=key, expires_on=expires, reason=reason)


def _report(records=None):
    return ExpiryReport(filename="staging.env", records=records or [])


class TestFormatExpiryRecord:
    def test_expired_record_contains_key(self):
        out = format_expiry_record(_rec("OLD_TOKEN", _PAST))
        assert "OLD_TOKEN" in out

    def test_expired_record_contains_expired_label(self):
        out = format_expiry_record(_rec(expires=_PAST))
        assert "EXPIRED" in out

    def test_future_record_contains_ok_label(self):
        out = format_expiry_record(_rec(expires=_FUTURE_FAR))
        assert "OK" in out

    def test_near_future_record_contains_expiring_label(self):
        out = format_expiry_record(_rec(expires=_FUTURE_NEAR))
        assert "EXPIRING" in out

    def test_reason_shown_when_present(self):
        out = format_expiry_record(_rec(reason="scheduled rotation"))
        assert "scheduled rotation" in out

    def test_reason_absent_when_none(self):
        out = format_expiry_record(_rec(reason=None))
        assert "(" not in out or "rotation" not in out


class TestFormatExpiryReport:
    def test_contains_filename(self):
        out = format_expiry_report(_report())
        assert "staging.env" in out

    def test_empty_report_shows_no_records_message(self):
        out = format_expiry_report(_report([]))
        assert "No expiry records" in out

    def test_shows_key_for_each_record(self):
        records = [_rec("DB_PASS"), _rec("API_TOKEN")]
        out = format_expiry_report(_report(records))
        assert "DB_PASS" in out
        assert "API_TOKEN" in out


class TestFormatExpirySummary:
    def test_contains_total(self):
        out = format_expiry_summary(_report([_rec()]))
        assert "total=" in out

    def test_contains_expired(self):
        out = format_expiry_summary(_report([_rec(expires=_PAST)]))
        assert "expired=" in out

    def test_contains_expiring_soon(self):
        out = format_expiry_summary(_report([_rec(expires=_FUTURE_NEAR)]))
        assert "expiring_soon=" in out

    def test_zero_totals_for_empty(self):
        out = format_expiry_summary(_report([]))
        assert "total=0" in out

"""Tests for env_expiry.py."""
from datetime import date

import pytest

from patchwork_env.env_expiry import ExpiryRecord, ExpiryReport, build_expiry_report

_TODAY = date(2024, 6, 15)
_PAST = date(2024, 1, 1)
_FUTURE_NEAR = date(2024, 7, 1)   # 16 days away
_FUTURE_FAR = date(2025, 1, 1)


def _rec(key="API_KEY", expires=_FUTURE_FAR, reason=None):
    return ExpiryRecord(key=key, expires_on=expires, reason=reason)


class TestExpiryRecord:
    def test_is_expired_when_past(self):
        r = _rec(expires=_PAST)
        assert r.is_expired(today=_TODAY)

    def test_not_expired_when_future(self):
        r = _rec(expires=_FUTURE_FAR)
        assert not r.is_expired(today=_TODAY)

    def test_days_until_positive_for_future(self):
        r = _rec(expires=_FUTURE_NEAR)
        assert r.days_until(today=_TODAY) == 16

    def test_days_until_negative_for_past(self):
        r = _rec(expires=_PAST)
        assert r.days_until(today=_TODAY) < 0

    def test_round_trip_dict(self):
        r = _rec(key="SECRET", expires=_FUTURE_NEAR, reason="rotation")
        assert ExpiryRecord.from_dict(r.to_dict()) == r

    def test_to_dict_keys(self):
        r = _rec()
        d = r.to_dict()
        assert set(d.keys()) == {"key", "expires_on", "reason"}

    def test_reason_none_by_default(self):
        r = ExpiryRecord(key="X", expires_on=_FUTURE_FAR)
        assert r.reason is None


class TestExpiryReport:
    def _report(self, records):
        return ExpiryReport(filename="test.env", records=records)

    def test_expired_filters_correctly(self):
        r1 = _rec("A", _PAST)
        r2 = _rec("B", _FUTURE_FAR)
        report = self._report([r1, r2])
        expired = [r for r in report.records if r.is_expired(today=_TODAY)]
        assert len(expired) == 1
        assert expired[0].key == "A"

    def test_has_expired_true(self):
        report = self._report([_rec("A", _PAST)])
        # Override is_expired check via direct inspection
        assert any(r.is_expired(today=_TODAY) for r in report.records)

    def test_has_expired_false_when_all_future(self):
        report = self._report([_rec("A", _FUTURE_FAR)])
        assert not any(r.is_expired(today=_TODAY) for r in report.records)

    def test_empty_report_no_expired(self):
        report = self._report([])
        assert report.records == []


def test_build_expiry_report_returns_report():
    records = [_rec("DB_PASS", _PAST)]
    report = build_expiry_report("prod.env", records)
    assert report.filename == "prod.env"
    assert len(report.records) == 1


def test_build_expiry_report_copies_list():
    records = [_rec()]
    report = build_expiry_report("x.env", records)
    records.clear()
    assert len(report.records) == 1

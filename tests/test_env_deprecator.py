"""Tests for env_deprecator and deprecation_formatter."""
import pytest
from patchwork_env.env_deprecator import (
    DeprecationRecord,
    DeprecationHit,
    DeprecationReport,
    DeprecationRegistry,
)
from patchwork_env.deprecation_formatter import (
    format_deprecation_report,
    format_deprecation_summary,
    format_registry,
)


def _entry(key: str, value: str = "val"):
    class _E:
        pass
    e = _E()
    e.key = key
    e.value = value
    return e


# --- DeprecationRecord ---

def test_record_to_dict_contains_key():
    rec = DeprecationRecord(key="OLD_KEY", reason="use NEW", replacement="NEW_KEY")
    d = rec.to_dict()
    assert d["key"] == "OLD_KEY"
    assert d["reason"] == "use NEW"
    assert d["replacement"] == "NEW_KEY"


def test_record_round_trip():
    rec = DeprecationRecord(key="FOO", reason="obsolete", replacement="BAR")
    assert DeprecationRecord.from_dict(rec.to_dict()) == rec


def test_record_defaults_none():
    rec = DeprecationRecord(key="X")
    assert rec.reason is None
    assert rec.replacement is None


# --- DeprecationRegistry ---

class TestDeprecationRegistry:
    def setup_method(self):
        self.reg = DeprecationRegistry()

    def test_register_stores_record(self):
        rec = self.reg.register("OLD_KEY")
        assert rec.key == "OLD_KEY"

    def test_key_normalised_to_upper(self):
        self.reg.register("old_key")
        assert self.reg.is_deprecated("OLD_KEY")

    def test_is_deprecated_false_for_unknown(self):
        assert not self.reg.is_deprecated("UNKNOWN")

    def test_unregister_removes_key(self):
        self.reg.register("GONE")
        self.reg.unregister("GONE")
        assert not self.reg.is_deprecated("GONE")

    def test_unregister_missing_is_noop(self):
        self.reg.unregister("NEVER_THERE")  # should not raise

    def test_get_returns_record(self):
        self.reg.register("FOO", reason="old")
        rec = self.reg.get("FOO")
        assert rec is not None
        assert rec.reason == "old"

    def test_all_records_lists_all(self):
        self.reg.register("A")
        self.reg.register("B")
        keys = [r.key for r in self.reg.all_records()]
        assert "A" in keys and "B" in keys


# --- scan ---

def test_scan_detects_deprecated_entry():
    reg = DeprecationRegistry()
    reg.register("OLD", reason="replaced")
    entries = [_entry("OLD"), _entry("FINE")]
    report = reg.scan(entries, filename="test.env")
    assert report.has_deprecated
    assert "OLD" in report.deprecated_keys


def test_scan_ignores_non_deprecated_entries():
    reg = DeprecationRegistry()
    reg.register("OLD")
    entries = [_entry("NEW"), _entry("OTHER")]
    report = reg.scan(entries, filename="test.env")
    assert not report.has_deprecated


# --- formatter ---

def test_format_report_contains_filename():
    reg = DeprecationRegistry()
    report = reg.scan([], filename="prod.env")
    out = format_deprecation_report(report)
    assert "prod.env" in out


def test_format_report_clean_shows_checkmark():
    reg = DeprecationRegistry()
    report = reg.scan([], filename="x.env")
    out = format_deprecation_report(report)
    assert "✔" in out


def test_format_report_shows_deprecated_key():
    reg = DeprecationRegistry()
    reg.register("OLD_TOKEN", reason="use JWT", replacement="JWT_SECRET")
    entries = [_entry("OLD_TOKEN")]
    report = reg.scan(entries, filename="x.env")
    out = format_deprecation_report(report)
    assert "OLD_TOKEN" in out
    assert "JWT_SECRET" in out


def test_format_summary_no_hits():
    reg = DeprecationRegistry()
    report = reg.scan([], filename="x.env")
    out = format_deprecation_summary(report)
    assert "no deprecated" in out


def test_format_summary_with_hits():
    reg = DeprecationRegistry()
    reg.register("OLD")
    report = reg.scan([_entry("OLD")], filename="x.env")
    out = format_deprecation_summary(report)
    assert "1" in out


def test_format_registry_empty():
    reg = DeprecationRegistry()
    out = format_registry(reg)
    assert "(none)" in out


def test_format_registry_shows_key():
    reg = DeprecationRegistry()
    reg.register("OLD_API_KEY", replacement="API_KEY")
    out = format_registry(reg)
    assert "OLD_API_KEY" in out
    assert "API_KEY" in out

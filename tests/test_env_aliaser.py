"""Tests for env_aliaser and alias_formatter."""
import pytest

from patchwork_env.parser import EnvEntry
from patchwork_env.env_aliaser import AliasRecord, AliasRegistry, AliasReport
from patchwork_env.alias_formatter import format_alias_report, format_alias_summary


def _entry(key: str, value: str) -> EnvEntry:
    return EnvEntry(key=key, value=value, raw_line=f"{key}={value}")


# ---------------------------------------------------------------------------
# AliasRegistry
# ---------------------------------------------------------------------------

class TestAliasRegistry:
    def test_register_creates_record(self):
        reg = AliasRegistry()
        record = reg.register("DATABASE_URL", "DB_URL", "DB")
        assert record.canonical == "DATABASE_URL"
        assert "DB_URL" in record.aliases
        assert "DB" in record.aliases

    def test_register_idempotent(self):
        reg = AliasRegistry()
        reg.register("DATABASE_URL", "DB_URL")
        reg.register("DATABASE_URL", "DB_URL")  # duplicate
        assert reg.records["DATABASE_URL"].aliases.count("DB_URL") == 1

    def test_unregister_removes_record(self):
        reg = AliasRegistry()
        reg.register("DATABASE_URL", "DB_URL")
        reg.unregister("DATABASE_URL")
        assert "DATABASE_URL" not in reg.records

    def test_unregister_missing_is_noop(self):
        reg = AliasRegistry()
        reg.unregister("NONEXISTENT")  # should not raise

    def test_lookup_canonical_returns_correct_key(self):
        reg = AliasRegistry()
        reg.register("SECRET_KEY", "APP_SECRET", "SECRET")
        assert reg.lookup_canonical("APP_SECRET") == "SECRET_KEY"
        assert reg.lookup_canonical("SECRET") == "SECRET_KEY"

    def test_lookup_canonical_returns_none_for_unknown(self):
        reg = AliasRegistry()
        reg.register("SECRET_KEY", "APP_SECRET")
        assert reg.lookup_canonical("UNKNOWN") is None


# ---------------------------------------------------------------------------
# AliasReport
# ---------------------------------------------------------------------------

@pytest.fixture
def registry():
    reg = AliasRegistry()
    reg.register("DATABASE_URL", "DB_URL", "DB_CONN")
    reg.register("SECRET_KEY", "APP_SECRET")
    return reg


@pytest.fixture
def entries():
    return [
        _entry("DATABASE_URL", "postgres://localhost/mydb"),
        _entry("DB_URL", "postgres://localhost/mydb"),
        _entry("SECRET_KEY", "supersecret"),
    ]


def test_resolved_includes_alias_hits(registry, entries):
    report = registry.scan(entries, filename=".env")
    resolved_aliases = [r[0] for r in report.resolved()]
    assert "DB_URL" in resolved_aliases


def test_resolved_excludes_missing_alias(registry, entries):
    # DB_CONN is not in entries, but DATABASE_URL is present — still reported
    report = registry.scan(entries, filename=".env")
    resolved_aliases = [r[0] for r in report.resolved()]
    assert "DB_CONN" in resolved_aliases  # value comes from canonical


def test_missing_canonicals_empty_when_all_present(registry, entries):
    report = registry.scan(entries, filename=".env")
    assert report.missing_canonicals() == []


def test_missing_canonicals_detected(registry):
    report = registry.scan([_entry("OTHER_KEY", "val")], filename=".env")
    missing = report.missing_canonicals()
    assert "DATABASE_URL" in missing
    assert "SECRET_KEY" in missing


# ---------------------------------------------------------------------------
# Formatter
# ---------------------------------------------------------------------------

def test_format_alias_report_contains_filename(registry, entries):
    report = registry.scan(entries, filename="production.env")
    output = format_alias_report(report)
    assert "production.env" in output


def test_format_alias_report_shows_resolved_alias(registry, entries):
    report = registry.scan(entries, filename=".env")
    output = format_alias_report(report)
    assert "DB_URL" in output


def test_format_alias_summary_contains_counts(registry, entries):
    report = registry.scan(entries, filename=".env")
    summary = format_alias_summary(report)
    assert "registered" in summary
    assert "resolved" in summary

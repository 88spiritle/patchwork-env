"""Tests for patchwork_env.encrypt_formatter."""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from patchwork_env.env_encryptr import EncryptedEntry, EncryptReport
from patchwork_env.encrypt_formatter import format_encrypt_report, format_encrypt_summary


@pytest.fixture
def sample_report() -> EncryptReport:
    entries = [
        EncryptedEntry(key="DB_HOST", token="abc123xyz==", backend="xor"),
        EncryptedEntry(key="API_SECRET", token="def456uvw==", backend="xor"),
    ]
    return EncryptReport(
        filename=".env.staging",
        entries=entries,
        passphrase_hint="team-vault",
    )


# ---------------------------------------------------------------------------
# format_encrypt_report
# ---------------------------------------------------------------------------

def test_format_report_contains_filename(sample_report):
    out = format_encrypt_report(sample_report)
    assert ".env.staging" in out


def test_format_report_shows_keys(sample_report):
    out = format_encrypt_report(sample_report)
    assert "DB_HOST" in out
    assert "API_SECRET" in out


def test_format_report_shows_hint(sample_report):
    out = format_encrypt_report(sample_report)
    assert "team-vault" in out


def test_format_report_shows_token_preview(sample_report):
    out = format_encrypt_report(sample_report)
    # Token is short enough to appear in full
    assert "abc123xyz" in out


def test_format_report_shows_backend(sample_report):
    out = format_encrypt_report(sample_report)
    assert "xor" in out


def test_format_report_no_hint_omits_hint_line():
    report = EncryptReport(
        filename=".env",
        entries=[EncryptedEntry(key="K", token="t", backend="xor")],
        passphrase_hint=None,
    )
    out = format_encrypt_report(report)
    assert "Hint" not in out


# ---------------------------------------------------------------------------
# format_encrypt_summary
# ---------------------------------------------------------------------------

def test_format_summary_contains_filename(sample_report):
    out = format_encrypt_summary(sample_report)
    assert ".env.staging" in out


def test_format_summary_shows_count(sample_report):
    out = format_encrypt_summary(sample_report)
    assert "2" in out


def test_format_summary_shows_backend(sample_report):
    out = format_encrypt_summary(sample_report)
    assert "xor" in out


def test_format_summary_empty_entries():
    report = EncryptReport(filename=".env", entries=[])
    out = format_encrypt_summary(report)
    assert "n/a" in out

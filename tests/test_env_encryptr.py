"""Tests for patchwork_env.env_encryptr."""
from __future__ import annotations

import pytest
from dataclasses import dataclass

from patchwork_env.env_encryptr import (
    _derive_key,
    _xor_encrypt,
    _xor_decrypt,
    encrypt_entries,
    decrypt_entry,
    EncryptedEntry,
    EncryptReport,
)


# ---------------------------------------------------------------------------
# Minimal stub for EnvEntry
# ---------------------------------------------------------------------------

@dataclass
class _Entry:
    key: str
    value: str


PASS = "s3cr3t"


# ---------------------------------------------------------------------------
# _derive_key
# ---------------------------------------------------------------------------

def test_derive_key_returns_32_bytes():
    assert len(_derive_key(PASS)) == 32


def test_derive_key_deterministic():
    assert _derive_key(PASS) == _derive_key(PASS)


def test_derive_key_differs_for_different_passphrases():
    assert _derive_key(PASS) != _derive_key("other")


# ---------------------------------------------------------------------------
# XOR round-trip
# ---------------------------------------------------------------------------

def test_xor_encrypt_returns_string():
    key = _derive_key(PASS)
    token = _xor_encrypt("hello", key)
    assert isinstance(token, str)


def test_xor_round_trip():
    key = _derive_key(PASS)
    original = "MY_SECRET_VALUE"
    assert _xor_decrypt(_xor_encrypt(original, key), key) == original


def test_xor_empty_string():
    key = _derive_key(PASS)
    assert _xor_decrypt(_xor_encrypt("", key), key) == ""


# ---------------------------------------------------------------------------
# encrypt_entries
# ---------------------------------------------------------------------------

@pytest.fixture
def entries():
    return [
        _Entry(key="DB_HOST", value="localhost"),
        _Entry(key="DB_PASS", value="hunter2"),
        _Entry(key="API_KEY", value="abc123"),
    ]


def test_encrypt_entries_returns_report(entries):
    report = encrypt_entries(entries, PASS, filename=".env.prod")
    assert isinstance(report, EncryptReport)


def test_encrypt_entries_count(entries):
    report = encrypt_entries(entries, PASS)
    assert report.total == len(entries)


def test_encrypt_entries_keys_preserved(entries):
    report = encrypt_entries(entries, PASS)
    keys = [e.key for e in report.entries]
    assert keys == ["DB_HOST", "DB_PASS", "API_KEY"]


def test_encrypt_entries_values_differ_from_originals(entries):
    report = encrypt_entries(entries, PASS)
    for enc, orig in zip(report.entries, entries):
        assert enc.token != orig.value


def test_encrypt_entries_passphrase_hint(entries):
    report = encrypt_entries(entries, PASS, passphrase_hint="ask-alice")
    assert report.passphrase_hint == "ask-alice"


# ---------------------------------------------------------------------------
# decrypt_entry
# ---------------------------------------------------------------------------

def test_decrypt_entry_xor_round_trip():
    entry = _Entry(key="X", value="plaintext")
    report = encrypt_entries([entry], PASS)
    enc = report.entries[0]
    assert enc.backend == "xor" or enc.backend == "fernet"
    assert decrypt_entry(enc, PASS) == "plaintext"


def test_decrypt_entry_wrong_passphrase_differs():
    entry = _Entry(key="X", value="secret")
    report = encrypt_entries([entry], PASS)
    enc = report.entries[0]
    if enc.backend == "xor":
        # XOR with wrong key gives garbled output, not the original
        assert decrypt_entry(enc, "wrongpass") != "secret"
    else:
        pytest.skip("fernet raises on wrong passphrase — covered separately")

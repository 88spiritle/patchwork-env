"""Lightweight symmetric encryption wrapper for .env values.

Uses Fernet (AES-128-CBC + HMAC-SHA256) from the *cryptography* package when
available; falls back to a simple XOR-based obfuscation so the module stays
importable in environments without the optional dependency.
"""
from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from an arbitrary passphrase via SHA-256."""
    return hashlib.sha256(passphrase.encode()).digest()


def _xor_encrypt(value: str, key: bytes) -> str:
    """Fallback XOR obfuscation – NOT cryptographically secure."""
    data = value.encode()
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return base64.urlsafe_b64encode(out).decode()


def _xor_decrypt(token: str, key: bytes) -> str:
    data = base64.urlsafe_b64decode(token.encode())
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return out.decode()


def _fernet_encrypt(value: str, key: bytes) -> str:
    from cryptography.fernet import Fernet
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key).encrypt(value.encode()).decode()


def _fernet_decrypt(token: str, key: bytes) -> str:
    from cryptography.fernet import Fernet
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key).decrypt(token.encode()).decode()


def _has_fernet() -> bool:
    try:
        import cryptography  # noqa: F401
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class EncryptedEntry:
    key: str
    token: str          # encrypted / obfuscated value
    backend: str        # 'fernet' | 'xor'

    def __repr__(self) -> str:  # pragma: no cover
        return f"EncryptedEntry(key={self.key!r}, backend={self.backend!r})"


@dataclass
class EncryptReport:
    filename: str
    entries: List[EncryptedEntry] = field(default_factory=list)
    passphrase_hint: Optional[str] = None

    @property
    def total(self) -> int:
        return len(self.entries)


def encrypt_entries(
    entries,
    passphrase: str,
    filename: str = "<unknown>",
    passphrase_hint: Optional[str] = None,
) -> EncryptReport:
    """Encrypt all entry values; returns an :class:`EncryptReport`."""
    key = _derive_key(passphrase)
    use_fernet = _has_fernet()
    backend = "fernet" if use_fernet else "xor"
    encrypt_fn = _fernet_encrypt if use_fernet else _xor_encrypt

    encrypted = [
        EncryptedEntry(key=e.key, token=encrypt_fn(e.value, key), backend=backend)
        for e in entries
    ]
    return EncryptReport(filename=filename, entries=encrypted, passphrase_hint=passphrase_hint)


def decrypt_entry(entry: EncryptedEntry, passphrase: str) -> str:
    """Decrypt a single :class:`EncryptedEntry` and return the plaintext value."""
    key = _derive_key(passphrase)
    if entry.backend == "fernet":
        return _fernet_decrypt(entry.token, key)
    return _xor_decrypt(entry.token, key)

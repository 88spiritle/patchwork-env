"""Tests for patchwork_env.env_encoder."""
import base64
import pytest

from patchwork_env.env_encoder import (
    Encoding,
    EncodedEntry,
    EncodeResult,
    _encode_value,
    _decode_value,
    encode_entries,
    decode_entries,
)


class _Entry:
    """Minimal stand-in for EnvEntry."""
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


def _entry(key: str = "MY_KEY", value: str = "hello") -> _Entry:
    return _Entry(key, value)


# ---------------------------------------------------------------------------
# _encode_value / _decode_value
# ---------------------------------------------------------------------------

def test_encode_base64_produces_valid_base64():
    result = _encode_value("hello", Encoding.BASE64)
    assert base64.b64decode(result.encode("ascii")).decode() == "hello"


def test_encode_hex_produces_valid_hex():
    result = _encode_value("hello", Encoding.HEX)
    assert bytes.fromhex(result).decode() == "hello"


def test_decode_base64_round_trip():
    encoded = _encode_value("secret_value", Encoding.BASE64)
    assert _decode_value(encoded, Encoding.BASE64) == "secret_value"


def test_decode_hex_round_trip():
    encoded = _encode_value("secret_value", Encoding.HEX)
    assert _decode_value(encoded, Encoding.HEX) == "secret_value"


def test_unsupported_encoding_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        _encode_value("x", "rot13")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# encode_entries
# ---------------------------------------------------------------------------

def test_encode_entries_returns_encode_result():
    entries = [_entry("A", "alpha"), _entry("B", "beta")]
    result = encode_entries(entries, Encoding.BASE64, filename=".env")
    assert isinstance(result, EncodeResult)


def test_encode_entries_total_encoded():
    entries = [_entry("A", "alpha"), _entry("B", "beta")]
    result = encode_entries(entries, Encoding.BASE64)
    assert result.total_encoded == 2


def test_encode_entries_preserves_key():
    result = encode_entries([_entry("MY_KEY", "val")], Encoding.HEX)
    assert result.entries[0].key == "MY_KEY"


def test_encode_entries_stores_original_value():
    result = encode_entries([_entry("K", "original")], Encoding.BASE64)
    assert result.entries[0].original_value == "original"


def test_encode_entries_encoded_value_differs_from_original():
    result = encode_entries([_entry("K", "plaintext")], Encoding.BASE64)
    assert result.entries[0].encoded_value != "plaintext"


def test_encode_entries_filename_propagated():
    result = encode_entries([_entry()], Encoding.HEX, filename="prod.env")
    assert result.filename == "prod.env"
    assert result.entries[0].filename == "prod.env"


# ---------------------------------------------------------------------------
# decode_entries
# ---------------------------------------------------------------------------

def test_decode_entries_round_trip_base64():
    original = [_entry("TOKEN", "my_secret_token")]
    encoded_result = encode_entries(original, Encoding.BASE64)
    # Build fake entries from encoded values
    encoded_as_entries = [
        _Entry(e.key, e.encoded_value) for e in encoded_result.entries
    ]
    decoded_result = decode_entries(encoded_as_entries, Encoding.BASE64)
    assert decoded_result.entries[0].encoded_value == "my_secret_token"


def test_decode_entries_round_trip_hex():
    original = [_entry("PWD", "p@ssw0rd!")]
    encoded_result = encode_entries(original, Encoding.HEX)
    encoded_as_entries = [
        _Entry(e.key, e.encoded_value) for e in encoded_result.entries
    ]
    decoded_result = decode_entries(encoded_as_entries, Encoding.HEX)
    assert decoded_result.entries[0].encoded_value == "p@ssw0rd!"


def test_decode_entries_total_encoded_count():
    entries = [_entry("A", base64.b64encode(b"alpha").decode()),
               _entry("B", base64.b64encode(b"beta").decode())]
    result = decode_entries(entries, Encoding.BASE64)
    assert result.total_encoded == 2

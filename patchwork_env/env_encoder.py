"""env_encoder: encode/decode .env entry values using base64 or hex."""
from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Encoding(str, Enum):
    BASE64 = "base64"
    HEX = "hex"


@dataclass
class EncodedEntry:
    key: str
    original_value: str
    encoded_value: str
    encoding: Encoding
    filename: str = ""

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"EncodedEntry(key={self.key!r}, encoding={self.encoding.value}, "
            f"filename={self.filename!r})"
        )


@dataclass
class EncodeResult:
    filename: str
    encoding: Encoding
    entries: List[EncodedEntry] = field(default_factory=list)

    @property
    def total_encoded(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"EncodeResult(filename={self.filename!r}, "
            f"encoding={self.encoding.value}, total={self.total_encoded})"
        )


def _encode_value(value: str, encoding: Encoding) -> str:
    raw = value.encode("utf-8")
    if encoding is Encoding.BASE64:
        return base64.b64encode(raw).decode("ascii")
    if encoding is Encoding.HEX:
        return raw.hex()
    raise ValueError(f"Unsupported encoding: {encoding}")


def _decode_value(value: str, encoding: Encoding) -> str:
    if encoding is Encoding.BASE64:
        return base64.b64decode(value.encode("ascii")).decode("utf-8")
    if encoding is Encoding.HEX:
        return bytes.fromhex(value).decode("utf-8")
    raise ValueError(f"Unsupported encoding: {encoding}")


def encode_entries(entries, encoding: Encoding, filename: str = "") -> EncodeResult:
    """Encode the value of every entry and return an EncodeResult."""
    result = EncodeResult(filename=filename, encoding=encoding)
    for entry in entries:
        encoded = _encode_value(entry.value, encoding)
        result.entries.append(
            EncodedEntry(
                key=entry.key,
                original_value=entry.value,
                encoded_value=encoded,
                encoding=encoding,
                filename=filename,
            )
        )
    return result


def decode_entries(entries, encoding: Encoding, filename: str = "") -> EncodeResult:
    """Decode previously-encoded values and return an EncodeResult."""
    result = EncodeResult(filename=filename, encoding=encoding)
    for entry in entries:
        decoded = _decode_value(entry.value, encoding)
        result.entries.append(
            EncodedEntry(
                key=entry.key,
                original_value=entry.value,
                encoded_value=decoded,
                encoding=encoding,
                filename=filename,
            )
        )
    return result

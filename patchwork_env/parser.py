"""Parser for .env files supporting comments, blank lines, and quoted values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_INLINE_COMMENT_RE = re.compile(r"(?<!\\)\s+#.*$")


def _strip_inline_comment(value: str) -> str:
    """Remove trailing inline comment from an unquoted value."""
    return _INLINE_COMMENT_RE.sub("", value).strip()


def _parse_value(raw: str) -> str:
    """Parse a raw value string, handling quotes and inline comments."""
    raw = raw.strip()
    if (raw.startswith('"') and raw.endswith('"')) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        return raw[1:-1]
    return _strip_inline_comment(raw)


@dataclass
class EnvEntry:
    key: str
    value: str
    comment: Optional[str] = None  # full-line comment or blank preserved as raw text
    raw_line: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnvEntry):
            return NotImplemented
        return self.key == other.key and self.value == other.value

    def __repr__(self) -> str:
        return f"EnvEntry(key={self.key!r}, value={self.value!r})"


@dataclass
class EnvFile:
    name: str
    entries: List[EnvEntry] = field(default_factory=list)
    _raw_lines: List[str] = field(default_factory=list, repr=False)

    @classmethod
    def from_text(cls, text: str, name: str = "<string>") -> "EnvFile":
        entries: List[EnvEntry] = []
        raw_lines = text.splitlines(keepends=True)
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                entries.append(EnvEntry(key="", value="", comment=line.rstrip("\n"), raw_line=line))
                continue
            if "=" not in stripped:
                continue
            key, _, raw_value = stripped.partition("=")
            entries.append(
                EnvEntry(key=key.strip(), value=_parse_value(raw_value), raw_line=line)
            )
        return cls(name=name, entries=entries, _raw_lines=raw_lines)

    @classmethod
    def from_path(cls, path: Path) -> "EnvFile":
        return cls.from_text(path.read_text(), name=str(path))

    def as_dict(self) -> dict:
        return {e.key: e.value for e in self.entries if e.key}

    def keys(self) -> List[str]:
        return [e.key for e in self.entries if e.key]

    def get(self, key: str) -> Optional[str]:
        for e in self.entries:
            if e.key == key:
                return e.value
        return None

    def __contains__(self, key: str) -> bool:
        return any(e.key == key for e in self.entries)

    def __repr__(self) -> str:
        return f"EnvFile(name={self.name!r}, entries={len(self.entries)})"

"""Parser for .env files — handles reading, tokenizing, and representing env entries."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


ENV_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$"
)
COMMENT_RE = re.compile(r"^\s*#.*$")


@dataclass
class EnvEntry:
    """Represents a single key-value pair from a .env file."""

    key: str
    value: str
    comment: Optional[str] = None  # inline comment stripped from value
    line_number: int = 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnvEntry):
            return NotImplemented
        return self.key == other.key and self.value == other.value

    def __repr__(self) -> str:
        return f"EnvEntry(key={self.key!r}, value={self.value!r})"


@dataclass
class EnvFile:
    """Parsed representation of an entire .env file."""

    path: Path
    entries: list[EnvEntry] = field(default_factory=list)
    raw_lines: list[str] = field(default_factory=list)

    @property
    def as_dict(self) -> dict[str, str]:
        return {entry.key: entry.value for entry in self.entries}

    def get(self, key: str) -> Optional[EnvEntry]:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None


def _strip_inline_comment(raw_value: str) -> tuple[str, Optional[str]]:
    """Separate the actual value from any trailing inline comment."""
    # Only strip unquoted inline comments
    if raw_value.startswith(("'", '"')):
        quote = raw_value[0]
        end = raw_value.rfind(quote, 1)
        if end != -1:
            return raw_value[1:end], None
        return raw_value, None

    if " #" in raw_value:
        value, _, comment = raw_value.partition(" #")
        return value.rstrip(), comment.strip()
    return raw_value.rstrip(), None


def parse_env_file(path: Path) -> EnvFile:
    """Read and parse a .env file from disk."""
    env_file = EnvFile(path=path)

    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    env_file.raw_lines = lines

    for lineno, line in enumerate(lines, start=1):
        if not line.strip() or COMMENT_RE.match(line):
            continue

        match = ENV_LINE_RE.match(line)
        if match:
            key = match.group("key")
            raw_value = match.group("value")
            value, comment = _strip_inline_comment(raw_value)
            env_file.entries.append(
                EnvEntry(key=key, value=value, comment=comment, line_number=lineno)
            )

    return env_file

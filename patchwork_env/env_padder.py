"""env_padder: align .env file values by padding keys to a uniform width."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry


@dataclass
class PaddedLine:
    original: EnvEntry
    padded_text: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"PaddedLine(key={self.original.key!r}, padded_text={self.padded_text!r})"


@dataclass
class PadResult:
    filename: str
    lines: List[PaddedLine] = field(default_factory=list)
    width: int = 0

    @property
    def total_entries(self) -> int:
        return len(self.lines)

    @property
    def was_already_aligned(self) -> bool:
        if not self.lines:
            return True
        return all(
            len(pl.original.key) == self.width for pl in self.lines
        )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PadResult(filename={self.filename!r}, "
            f"width={self.width}, entries={self.total_entries})"
        )


def pad_entries(entries: List[EnvEntry], filename: str = "") -> PadResult:
    """Return a PadResult where every KEY is left-padded to the same width."""
    if not entries:
        return PadResult(filename=filename, lines=[], width=0)

    width = max(len(e.key) for e in entries)
    lines: List[PaddedLine] = []
    for entry in entries:
        padded_key = entry.key.ljust(width)
        padded_text = f"{padded_key} = {entry.value}"
        lines.append(PaddedLine(original=entry, padded_text=padded_text))

    return PadResult(filename=filename, lines=lines, width=width)

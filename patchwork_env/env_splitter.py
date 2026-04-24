"""Split a flat list of EnvEntry objects into named sections by prefix."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from patchwork_env.parser import EnvEntry


@dataclass
class EnvSection:
    """A named group of entries sharing a common prefix."""

    name: str
    prefix: str
    entries: List[EnvEntry] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"EnvSection(name={self.name!r}, prefix={self.prefix!r}, count={len(self.entries)})"


@dataclass
class SplitResult:
    """Outcome of splitting entries into sections."""

    filename: str
    sections: List[EnvSection] = field(default_factory=list)
    uncategorised: List[EnvEntry] = field(default_factory=list)

    @property
    def section_names(self) -> List[str]:
        return [s.name for s in self.sections]

    @property
    def total_entries(self) -> int:
        return sum(len(s.entries) for s in self.sections) + len(self.uncategorised)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SplitResult(filename={self.filename!r}, "
            f"sections={len(self.sections)}, "
            f"uncategorised={len(self.uncategorised)})"
        )


def split_by_prefixes(
    entries: Sequence[EnvEntry],
    prefixes: Sequence[str],
    filename: str = "<unknown>",
) -> SplitResult:
    """Partition *entries* into sections whose keys start with one of *prefixes*.

    Entries that match no prefix land in ``SplitResult.uncategorised``.  When a
    key matches multiple prefixes the *longest* prefix wins.
    """
    sorted_prefixes = sorted(prefixes, key=len, reverse=True)
    bucket: Dict[str, EnvSection] = {
        p: EnvSection(name=p.rstrip("_").upper(), prefix=p) for p in sorted_prefixes
    }
    result = SplitResult(filename=filename)

    for entry in entries:
        matched = False
        for prefix in sorted_prefixes:
            if entry.key.upper().startswith(prefix.upper()):
                bucket[prefix].entries.append(entry)
                matched = True
                break
        if not matched:
            result.uncategorised.append(entry)

    result.sections = [bucket[p] for p in sorted_prefixes if bucket[p].entries]
    return result

"""env_stripper: remove entries matching a set of keys from an env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence

from patchwork_env.parser import EnvEntry


@dataclass
class StripRecord:
    """Record of a single key that was stripped."""
    key: str
    value: str
    filename: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"StripRecord(key={self.key!r}, filename={self.filename!r})"


@dataclass
class StripResult:
    """Outcome of a strip operation."""
    filename: str
    kept: List[EnvEntry] = field(default_factory=list)
    stripped: List[StripRecord] = field(default_factory=list)

    @property
    def total_stripped(self) -> int:
        return len(self.stripped)

    @property
    def was_clean(self) -> bool:
        """True when no entries were removed."""
        return self.total_stripped == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"StripResult(filename={self.filename!r}, "
            f"kept={len(self.kept)}, stripped={self.total_stripped})"
        )


def strip_keys(
    entries: Sequence[EnvEntry],
    keys_to_remove: Sequence[str],
    filename: str = "<unknown>",
) -> StripResult:
    """Return a StripResult with matching keys removed.

    Matching is case-insensitive against the canonical upper-cased key.
    """
    normalised = {k.strip().upper() for k in keys_to_remove}
    result = StripResult(filename=filename)

    for entry in entries:
        if entry.key is not None and entry.key.upper() in normalised:
            result.stripped.append(
                StripRecord(
                    key=entry.key,
                    value=entry.value or "",
                    filename=filename,
                )
            )
        else:
            result.kept.append(entry)

    return result

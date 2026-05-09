"""env_selector: filter and select env entries by multiple criteria."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from patchwork_env.parser import EnvEntry


@dataclass
class SelectionCriteria:
    """Criteria used to select entries."""
    keys: Optional[List[str]] = None          # exact key match (upper-cased)
    prefix: Optional[str] = None              # key starts-with prefix
    suffix: Optional[str] = None              # key ends-with suffix
    has_value: Optional[bool] = None          # True = non-empty, False = empty
    value_contains: Optional[str] = None      # substring in value

    def __repr__(self) -> str:  # pragma: no cover
        parts = []
        if self.keys:
            parts.append(f"keys={self.keys!r}")
        if self.prefix:
            parts.append(f"prefix={self.prefix!r}")
        if self.suffix:
            parts.append(f"suffix={self.suffix!r}")
        if self.has_value is not None:
            parts.append(f"has_value={self.has_value}")
        if self.value_contains:
            parts.append(f"value_contains={self.value_contains!r}")
        return f"SelectionCriteria({', '.join(parts)})"


@dataclass
class SelectionResult:
    """Result of a selection operation."""
    filename: str
    selected: List[EnvEntry] = field(default_factory=list)
    excluded: List[EnvEntry] = field(default_factory=list)

    @property
    def total_selected(self) -> int:
        return len(self.selected)

    @property
    def total_excluded(self) -> int:
        return len(self.excluded)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SelectionResult(filename={self.filename!r}, "
            f"selected={self.total_selected}, excluded={self.total_excluded})"
        )


def _matches(entry: EnvEntry, criteria: SelectionCriteria) -> bool:
    key = entry.key.upper()

    if criteria.keys is not None:
        if key not in [k.upper() for k in criteria.keys]:
            return False

    if criteria.prefix is not None:
        if not key.startswith(criteria.prefix.upper()):
            return False

    if criteria.suffix is not None:
        if not key.endswith(criteria.suffix.upper()):
            return False

    if criteria.has_value is not None:
        non_empty = bool(entry.value and entry.value.strip())
        if criteria.has_value != non_empty:
            return False

    if criteria.value_contains is not None:
        if criteria.value_contains not in (entry.value or ""):
            return False

    return True


def select_entries(
    entries: Sequence[EnvEntry],
    criteria: SelectionCriteria,
    filename: str = "<unknown>",
) -> SelectionResult:
    result = SelectionResult(filename=filename)
    for entry in entries:
        if _matches(entry, criteria):
            result.selected.append(entry)
        else:
            result.excluded.append(entry)
    return result

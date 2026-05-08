"""Registry that maps file extensions / format names to export formatter callables."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class FormatterRecord:
    name: str
    extension: str
    description: str
    formatter: Callable

    def __repr__(self) -> str:  # pragma: no cover
        return f"FormatterRecord(name={self.name!r}, extension={self.extension!r})"


class FormatterRegistry:
    """Holds named formatter callables keyed by format name."""

    def __init__(self) -> None:
        self._records: Dict[str, FormatterRecord] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        extension: str,
        description: str,
        formatter: Callable,
    ) -> FormatterRecord:
        record = FormatterRecord(
            name=name.lower(),
            extension=extension.lstrip(".").lower(),
            description=description,
            formatter=formatter,
        )
        self._records[record.name] = record
        return record

    def unregister(self, name: str) -> None:
        self._records.pop(name.lower(), None)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, name: str) -> Optional[FormatterRecord]:
        return self._records.get(name.lower())

    def names(self) -> List[str]:
        return sorted(self._records.keys())

    def all(self) -> List[FormatterRecord]:
        return [self._records[n] for n in self.names()]

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, name: str) -> bool:
        return name.lower() in self._records

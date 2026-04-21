"""Freeze a set of env entries so their values cannot be overridden during a merge."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class FrozenKey:
    key: str
    frozen_value: str
    reason: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        tag = f" ({self.reason})" if self.reason else ""
        return f"FrozenKey({self.key!r}{tag})"


@dataclass
class FreezeResult:
    entries: List[EnvEntry]
    frozen_keys: List[FrozenKey] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)

    @property
    def total_frozen(self) -> int:
        return len(self.frozen_keys)

    @property
    def total_skipped(self) -> int:
        return len(self.skipped_keys)


class FreezeRegistry:
    """Maintains a registry of keys whose values are frozen."""

    def __init__(self) -> None:
        self._frozen: dict[str, FrozenKey] = {}

    def freeze(self, key: str, value: str, reason: Optional[str] = None) -> FrozenKey:
        record = FrozenKey(key=key, frozen_value=value, reason=reason)
        self._frozen[key] = record
        return record

    def unfreeze(self, key: str) -> None:
        self._frozen.pop(key, None)

    def is_frozen(self, key: str) -> bool:
        return key in self._frozen

    def get(self, key: str) -> Optional[FrozenKey]:
        return self._frozen.get(key)

    @property
    def all_frozen(self) -> List[FrozenKey]:
        return list(self._frozen.values())

    def apply(self, entries: List[EnvEntry]) -> FreezeResult:
        """Return a new list of entries with frozen values enforced."""
        result_entries: List[EnvEntry] = []
        frozen_keys: List[FrozenKey] = []
        skipped_keys: List[str] = []

        for entry in entries:
            if entry.key and self.is_frozen(entry.key):
                record = self._frozen[entry.key]
                if entry.value != record.frozen_value:
                    skipped_keys.append(entry.key)
                    enforced = EnvEntry(
                        key=entry.key,
                        value=record.frozen_value,
                        comment=entry.comment,
                        raw_line=entry.raw_line,
                    )
                    result_entries.append(enforced)
                    frozen_keys.append(record)
                else:
                    result_entries.append(entry)
                    frozen_keys.append(record)
            else:
                result_entries.append(entry)

        return FreezeResult(
            entries=result_entries,
            frozen_keys=frozen_keys,
            skipped_keys=skipped_keys,
        )

"""Scope-based key filtering: restrict or expose keys by named scope."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class ScopeRecord:
    scope: str
    keys: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScopeRecord(scope={self.scope!r}, keys={self.keys})"


@dataclass
class ScopeResult:
    filename: str
    scope: str
    included: List[EnvEntry] = field(default_factory=list)
    excluded: List[EnvEntry] = field(default_factory=list)

    @property
    def total_included(self) -> int:
        return len(self.included)

    @property
    def total_excluded(self) -> int:
        return len(self.excluded)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"ScopeResult(scope={self.scope!r}, "
            f"included={self.total_included}, excluded={self.total_excluded})"
        )


class ScopeRegistry:
    def __init__(self) -> None:
        self._scopes: dict[str, ScopeRecord] = {}

    def define(self, scope: str, keys: List[str]) -> ScopeRecord:
        normalised = [k.upper() for k in keys]
        record = ScopeRecord(scope=scope, keys=normalised)
        self._scopes[scope] = record
        return record

    def remove(self, scope: str) -> None:
        self._scopes.pop(scope, None)

    def get(self, scope: str) -> Optional[ScopeRecord]:
        return self._scopes.get(scope)

    def all_scopes(self) -> List[str]:
        return list(self._scopes.keys())

    def apply(
        self, scope: str, entries: List[EnvEntry], filename: str = "<unknown>"
    ) -> ScopeResult:
        record = self._scopes.get(scope)
        allowed: set[str] = set(record.keys) if record else set()
        included, excluded = [], []
        for entry in entries:
            if entry.key and entry.key.upper() in allowed:
                included.append(entry)
            else:
                excluded.append(entry)
        return ScopeResult(
            filename=filename,
            scope=scope,
            included=included,
            excluded=excluded,
        )

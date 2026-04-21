"""env_aliaser.py — map canonical key names to one or more aliases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class AliasRecord:
    canonical: str
    aliases: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return f"AliasRecord(canonical={self.canonical!r}, aliases={self.aliases!r})"


@dataclass
class AliasReport:
    entries: List[EnvEntry]
    registry: "AliasRegistry"
    filename: str = "<unknown>"

    def resolved(self) -> List[tuple]:
        """Return (alias_key, canonical_key, value) for every alias hit."""
        result = []
        entry_map = {e.key: e for e in self.entries}
        for record in self.registry.records.values():
            canonical_entry = entry_map.get(record.canonical)
            if canonical_entry is None:
                continue
            for alias in record.aliases:
                if alias in entry_map:
                    result.append((alias, record.canonical, entry_map[alias].value))
                else:
                    result.append((alias, record.canonical, canonical_entry.value))
        return result

    def missing_canonicals(self) -> List[str]:
        entry_keys = {e.key for e in self.entries}
        return [
            record.canonical
            for record in self.registry.records.values()
            if record.canonical not in entry_keys
        ]


class AliasRegistry:
    def __init__(self) -> None:
        self.records: Dict[str, AliasRecord] = {}

    def register(self, canonical: str, *aliases: str) -> AliasRecord:
        if canonical not in self.records:
            self.records[canonical] = AliasRecord(canonical=canonical)
        record = self.records[canonical]
        for alias in aliases:
            if alias not in record.aliases:
                record.aliases.append(alias)
        return record

    def unregister(self, canonical: str) -> None:
        self.records.pop(canonical, None)

    def lookup_canonical(self, alias: str) -> Optional[str]:
        for record in self.records.values():
            if alias in record.aliases:
                return record.canonical
        return None

    def scan(self, entries: List[EnvEntry], filename: str = "<unknown>") -> AliasReport:
        return AliasReport(entries=entries, registry=self, filename=filename)

"""Tag .env entries with arbitrary labels for grouping and filtering."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set
from patchwork_env.parser import EnvEntry


@dataclass
class TaggedEntry:
    entry: EnvEntry
    tags: Set[str] = field(default_factory=set)

    def __repr__(self) -> str:
        return f"TaggedEntry(key={self.entry.key!r}, tags={sorted(self.tags)})"


@dataclass
class TagRegistry:
    name: str
    _map: Dict[str, Set[str]] = field(default_factory=dict, repr=False)

    def tag(self, key: str, *tags: str) -> None:
        """Add one or more tags to a key."""
        self._map.setdefault(key, set()).update(tags)

    def untag(self, key: str, *tags: str) -> None:
        """Remove tags from a key; silently ignores missing tags."""
        if key in self._map:
            self._map[key].difference_update(tags)
            if not self._map[key]:
                del self._map[key]

    def tags_for(self, key: str) -> Set[str]:
        return set(self._map.get(key, set()))

    def keys_for_tag(self, tag: str) -> List[str]:
        return [k for k, tags in self._map.items() if tag in tags]

    def to_dict(self) -> dict:
        return {"name": self.name, "tags": {k: sorted(v) for k, v in self._map.items()}}

    @classmethod
    def from_dict(cls, data: dict) -> "TagRegistry":
        reg = cls(name=data["name"])
        for key, tags in data.get("tags", {}).items():
            reg.tag(key, *tags)
        return reg


def apply_tags(entries: List[EnvEntry], registry: TagRegistry) -> List[TaggedEntry]:
    """Annotate a list of EnvEntry objects with tags from the registry."""
    return [TaggedEntry(entry=e, tags=registry.tags_for(e.key)) for e in entries]

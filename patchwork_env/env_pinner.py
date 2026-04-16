"""Pin specific env keys to fixed values across environments."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from patchwork_env.parser import EnvEntry


@dataclass
class PinnedKey:
    key: str
    value: str
    reason: Optional[str] = None

    def __repr__(self) -> str:
        return f"PinnedKey({self.key!r}={self.value!r})"


@dataclass
class PinRegistry:
    name: str
    pins: Dict[str, PinnedKey] = field(default_factory=dict)

    def pin(self, key: str, value: str, reason: Optional[str] = None) -> None:
        self.pins[key] = PinnedKey(key=key, value=value, reason=reason)

    def unpin(self, key: str) -> None:
        self.pins.pop(key, None)

    def is_pinned(self, key: str) -> bool:
        return key in self.pins

    def apply(self, entries: List[EnvEntry]) -> List[EnvEntry]:
        """Return entries with pinned keys overridden."""
        result = []
        for entry in entries:
            if entry.key and entry.key in self.pins:
                pinned = self.pins[entry.key]
                result.append(EnvEntry(
                    key=entry.key,
                    value=pinned.value,
                    comment=entry.comment,
                    raw=entry.raw,
                ))
            else:
                result.append(entry)
        return result

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "pins": {
                k: {"value": p.value, "reason": p.reason}
                for k, p in self.pins.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PinRegistry":
        reg = cls(name=data["name"])
        for key, meta in data.get("pins", {}).items():
            reg.pin(key, meta["value"], meta.get("reason"))
        return reg

"""Environment profile management: named sets of per-environment overrides."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class EnvProfile:
    """A named profile holding key→value overrides for a specific environment."""

    name: str
    environment: str
    overrides: Dict[str, str] = field(default_factory=dict)

    def set(self, key: str, value: str) -> None:
        """Add or update an override."""
        self.overrides[key] = value

    def unset(self, key: str) -> None:
        """Remove an override if present."""
        self.overrides.pop(key, None)

    def apply(self, entries: List[EnvEntry]) -> List[EnvEntry]:
        """Return a new list of EnvEntry with profile overrides applied."""
        result: List[EnvEntry] = []
        seen: Dict[str, int] = {}
        for entry in entries:
            idx = len(result)
            result.append(entry)
            if entry.key is not None:
                seen[entry.key] = idx
        for key, value in self.overrides.items():
            new_entry = EnvEntry(key=key, value=value, comment=None, raw=f"{key}={value}")
            if key in seen:
                result[seen[key]] = new_entry
            else:
                result.append(new_entry)
        return result

    def to_dict(self) -> dict:
        return {"name": self.name, "environment": self.environment, "overrides": dict(self.overrides)}

    @classmethod
    def from_dict(cls, data: dict) -> "EnvProfile":
        return cls(name=data["name"], environment=data["environment"], overrides=dict(data.get("overrides", {})))

    def __repr__(self) -> str:  # pragma: no cover
        return f"EnvProfile(name={self.name!r}, environment={self.environment!r}, overrides={len(self.overrides)} keys)"


class ProfileRegistry:
    """In-memory registry of named profiles."""

    def __init__(self) -> None:
        self._profiles: Dict[str, EnvProfile] = {}

    def register(self, profile: EnvProfile) -> None:
        self._profiles[profile.name] = profile

    def get(self, name: str) -> Optional[EnvProfile]:
        return self._profiles.get(name)

    def list_names(self) -> List[str]:
        return sorted(self._profiles.keys())

    def remove(self, name: str) -> bool:
        if name in self._profiles:
            del self._profiles[name]
            return True
        return False

    def to_dict(self) -> dict:
        return {name: p.to_dict() for name, p in self._profiles.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "ProfileRegistry":
        reg = cls()
        for raw in data.values():
            reg.register(EnvProfile.from_dict(raw))
        return reg

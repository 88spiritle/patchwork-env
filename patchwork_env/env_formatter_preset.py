"""Preset formatter configurations for common output scenarios."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class FormatterPreset:
    """A named collection of formatter options."""

    name: str
    description: str
    show_values: bool = True
    redact_sensitive: bool = False
    max_value_length: Optional[int] = None
    include_metadata: bool = False
    color: bool = True
    tags: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FormatterPreset(name={self.name!r}, "
            f"redact_sensitive={self.redact_sensitive}, "
            f"max_value_length={self.max_value_length})"
        )


class PresetRegistry:
    """Registry of named FormatterPreset instances."""

    def __init__(self) -> None:
        self._presets: Dict[str, FormatterPreset] = {}

    def register(self, preset: FormatterPreset) -> FormatterPreset:
        key = preset.name.lower()
        self._presets[key] = preset
        return preset

    def get(self, name: str) -> Optional[FormatterPreset]:
        return self._presets.get(name.lower())

    def all(self) -> List[FormatterPreset]:
        return list(self._presets.values())

    def names(self) -> List[str]:
        return [p.name for p in self._presets.values()]

    def remove(self, name: str) -> bool:
        key = name.lower()
        if key in self._presets:
            del self._presets[key]
            return True
        return False

    def __len__(self) -> int:
        return len(self._presets)


# Built-in presets
DEFAULT_PRESETS: List[FormatterPreset] = [
    FormatterPreset(
        name="verbose",
        description="Show all fields including metadata",
        show_values=True,
        redact_sensitive=False,
        include_metadata=True,
        tags=["debug"],
    ),
    FormatterPreset(
        name="safe",
        description="Redact sensitive values before display",
        show_values=True,
        redact_sensitive=True,
        tags=["security", "ci"],
    ),
    FormatterPreset(
        name="compact",
        description="Truncate long values for compact output",
        show_values=True,
        redact_sensitive=False,
        max_value_length=40,
        include_metadata=False,
        tags=["summary"],
    ),
    FormatterPreset(
        name="keys-only",
        description="Show only keys, hide all values",
        show_values=False,
        redact_sensitive=False,
        tags=["audit"],
    ),
]


def build_default_registry() -> PresetRegistry:
    """Return a PresetRegistry pre-loaded with built-in presets."""
    reg = PresetRegistry()
    for p in DEFAULT_PRESETS:
        reg.register(p)
    return reg

"""Attach human-readable annotations (comments) to individual env keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class AnnotatedEntry:
    entry: EnvEntry
    annotation: str

    def __repr__(self) -> str:  # pragma: no cover
        return f"AnnotatedEntry(key={self.entry.key!r}, annotation={self.annotation!r})"


@dataclass
class AnnotationRegistry:
    name: str
    _annotations: Dict[str, str] = field(default_factory=dict, repr=False)

    def annotate(self, key: str, text: str) -> None:
        """Set or replace the annotation for *key*."""
        self._annotations[key.upper()] = text

    def remove(self, key: str) -> None:
        """Remove the annotation for *key* (no-op if absent)."""
        self._annotations.pop(key.upper(), None)

    def get(self, key: str) -> Optional[str]:
        """Return the annotation for *key*, or ``None`` if not annotated."""
        return self._annotations.get(key.upper())

    def annotated_keys(self) -> List[str]:
        """Return all keys that have an annotation."""
        return list(self._annotations.keys())

    def apply(self, entries: List[EnvEntry]) -> List[AnnotatedEntry]:
        """Pair every entry with its annotation (empty string if none)."""
        return [
            AnnotatedEntry(
                entry=e,
                annotation=self._annotations.get(e.key.upper(), ""),
            )
            for e in entries
        ]

    def to_dict(self) -> dict:
        return {"name": self.name, "annotations": dict(self._annotations)}

    @classmethod
    def from_dict(cls, data: dict) -> "AnnotationRegistry":
        reg = cls(name=data["name"])
        for k, v in data.get("annotations", {}).items():
            reg._annotations[k] = v
        return reg

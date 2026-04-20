"""Preview the result of a merge without writing to disk."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from patchwork_env.parser import EnvEntry
from patchwork_env.resolver import Resolution, ResolutionStrategy


@dataclass
class PreviewLine:
    key: str
    value: str
    strategy: ResolutionStrategy
    comment: str = ""

    def __repr__(self) -> str:  # pragma: no cover
        return f"PreviewLine({self.key!r}, strategy={self.strategy.name})"


@dataclass
class MergePreview:
    base_name: str
    target_name: str
    lines: List[PreviewLine] = field(default_factory=list)

    # --- convenience accessors ---

    def kept(self) -> List[PreviewLine]:
        """Lines resolved by USE_BASE."""
        return [l for l in self.lines if l.strategy == ResolutionStrategy.USE_BASE]

    def overridden(self) -> List[PreviewLine]:
        """Lines resolved by USE_TARGET."""
        return [l for l in self.lines if l.strategy == ResolutionStrategy.USE_TARGET]

    def added(self) -> List[PreviewLine]:
        """Lines that are new (only in target)."""
        return [l for l in self.lines if l.strategy == ResolutionStrategy.ADD]

    def removed_keys(self) -> List[PreviewLine]:
        """Lines that will be dropped."""
        return [l for l in self.lines if l.strategy == ResolutionStrategy.REMOVE]


def build_preview(resolution: Resolution) -> MergePreview:
    """Convert a *Resolution* into a human-readable *MergePreview*."""
    preview = MergePreview(
        base_name=resolution.base_name,
        target_name=resolution.target_name,
    )

    for diff_entry, strategy in resolution.decisions.items():
        base_entry: EnvEntry | None = resolution.base_map.get(diff_entry)
        target_entry: EnvEntry | None = resolution.target_map.get(diff_entry)

        if strategy == ResolutionStrategy.REMOVE:
            entry = base_entry or target_entry
            value = entry.value if entry else ""
        elif strategy == ResolutionStrategy.USE_TARGET:
            entry = target_entry
            value = entry.value if entry else ""
        elif strategy == ResolutionStrategy.ADD:
            entry = target_entry
            value = entry.value if entry else ""
        else:  # USE_BASE
            entry = base_entry
            value = entry.value if entry else ""

        comment = entry.comment if entry and entry.comment else ""
        preview.lines.append(
            PreviewLine(key=diff_entry, value=value, strategy=strategy, comment=comment)
        )

    return preview

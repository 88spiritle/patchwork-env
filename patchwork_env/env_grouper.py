"""Group .env entries by prefix or custom label for organized output."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from patchwork_env.parser import EnvEntry


@dataclass
class EntryGroup:
    label: str
    entries: List[EnvEntry] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"EntryGroup(label={self.label!r}, count={len(self.entries)})"


def group_by_prefix(entries: List[EnvEntry], sep: str = "_") -> Dict[str, EntryGroup]:
    """Group entries by the first segment of their key split on *sep*."""
    groups: Dict[str, EntryGroup] = {}
    for entry in entries:
        if entry.key is None:
            continue
        prefix = entry.key.split(sep)[0] if sep in entry.key else entry.key
        if prefix not in groups:
            groups[prefix] = EntryGroup(label=prefix)
        groups[prefix].entries.append(entry)
    return groups


def group_by_label(entries: List[EnvEntry], mapping: Dict[str, str]) -> Dict[str, EntryGroup]:
    """Group entries using an explicit key->label mapping. Unmapped keys go to 'other'."""
    groups: Dict[str, EntryGroup] = {}
    for entry in entries:
        if entry.key is None:
            continue
        label = mapping.get(entry.key, "other")
        if label not in groups:
            groups[label] = EntryGroup(label=label)
        groups[label].entries.append(entry)
    return groups


def flat_sorted_groups(groups: Dict[str, EntryGroup]) -> List[EntryGroup]:
    """Return groups sorted alphabetically by label."""
    return [groups[k] for k in sorted(groups)]

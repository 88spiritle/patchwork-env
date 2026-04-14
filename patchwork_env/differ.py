"""Diff logic for comparing .env files across environments."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from .parser import EnvFile


class DiffStatus(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class DiffEntry:
    key: str
    status: DiffStatus
    base_value: Optional[str] = None
    target_value: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f"DiffEntry(key={self.key!r}, status={self.status.value}, "
            f"base={self.base_value!r}, target={self.target_value!r})"
        )


@dataclass
class EnvDiff:
    base_name: str
    target_name: str
    entries: List[DiffEntry] = field(default_factory=list)

    @property
    def added(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == DiffStatus.ADDED]

    @property
    def removed(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == DiffStatus.REMOVED]

    @property
    def modified(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == DiffStatus.MODIFIED]

    @property
    def unchanged(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == DiffStatus.UNCHANGED]

    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)


def diff_env_files(base: EnvFile, target: EnvFile) -> EnvDiff:
    """Compare two EnvFile instances and return an EnvDiff."""
    base_dict: Dict[str, str] = base.as_dict()
    target_dict: Dict[str, str] = target.as_dict()

    all_keys = sorted(set(base_dict) | set(target_dict))
    entries: List[DiffEntry] = []

    for key in all_keys:
        in_base = key in base_dict
        in_target = key in target_dict

        if in_base and not in_target:
            entries.append(DiffEntry(key, DiffStatus.REMOVED, base_value=base_dict[key]))
        elif in_target and not in_base:
            entries.append(DiffEntry(key, DiffStatus.ADDED, target_value=target_dict[key]))
        elif base_dict[key] != target_dict[key]:
            entries.append(
                DiffEntry(
                    key,
                    DiffStatus.MODIFIED,
                    base_value=base_dict[key],
                    target_value=target_dict[key],
                )
            )
        else:
            entries.append(
                DiffEntry(
                    key,
                    DiffStatus.UNCHANGED,
                    base_value=base_dict[key],
                    target_value=target_dict[key],
                )
            )

    return EnvDiff(base_name=base.path or "base", target_name=target.path or "target", entries=entries)

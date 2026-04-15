"""Conflict resolution strategies for reconciling differing env values."""

from enum import Enum
from typing import Dict, List, Optional

from patchwork_env.differ import DiffEntry, DiffStatus, EnvDiff
from patchwork_env.parser import EnvEntry, EnvFile


class ResolutionStrategy(Enum):
    USE_BASE = "use_base"
    USE_TARGET = "use_target"
    SKIP = "skip"


class Resolution:
    def __init__(self, key: str, strategy: ResolutionStrategy, value: Optional[str] = None):
        self.key = key
        self.strategy = strategy
        self.value = value

    def __repr__(self) -> str:
        return f"Resolution(key={self.key!r}, strategy={self.strategy.value}, value={self.value!r})"


def resolve_diff(
    diff: EnvDiff,
    resolutions: Dict[str, ResolutionStrategy],
) -> EnvFile:
    """Apply resolutions to a diff and return a reconciled EnvFile."""
    base_dict = diff.base.as_dict()
    target_dict = diff.target.as_dict()
    entries: List[EnvEntry] = []

    # Collect all keys across base and target
    all_keys: List[str] = []
    seen = set()
    for entry in diff.base.entries:
        if entry.key and entry.key not in seen:
            all_keys.append(entry.key)
            seen.add(entry.key)
    for entry in diff.target.entries:
        if entry.key and entry.key not in seen:
            all_keys.append(entry.key)
            seen.add(entry.key)

    for key in all_keys:
        strategy = resolutions.get(key, ResolutionStrategy.USE_TARGET)

        if strategy == ResolutionStrategy.SKIP:
            continue
        elif strategy == ResolutionStrategy.USE_BASE:
            if key in base_dict:
                entries.append(EnvEntry(key=key, value=base_dict[key]))
        else:  # USE_TARGET
            if key in target_dict:
                entries.append(EnvEntry(key=key, value=target_dict[key]))
            elif key in base_dict:
                entries.append(EnvEntry(key=key, value=base_dict[key]))

    return EnvFile(name="resolved", entries=entries)


def auto_resolve(
    diff: EnvDiff,
    default_strategy: ResolutionStrategy = ResolutionStrategy.USE_TARGET,
) -> EnvFile:
    """Automatically resolve all conflicts using the given default strategy."""
    resolutions: Dict[str, ResolutionStrategy] = {}
    for entry in diff.modified:
        resolutions[entry.key] = default_strategy
    return resolve_diff(diff, resolutions)

"""Migrate keys between environments using a rename map."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from patchwork_env.parser import EnvEntry


@dataclass
class MigrationRule:
    """A single rename/transform rule for migration."""
    old_key: str
    new_key: str
    transform: Optional[str] = None  # 'upper', 'lower', or None

    def __repr__(self) -> str:
        arrow = f"{self.old_key} -> {self.new_key}"
        if self.transform:
            arrow += f" [{self.transform}]"
        return f"MigrationRule({arrow})"


@dataclass
class MigrationResult:
    source_file: str
    rules_applied: List[MigrationRule] = field(default_factory=list)
    migrated: List[EnvEntry] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)
    unmatched_keys: List[str] = field(default_factory=list)

    @property
    def total_migrated(self) -> int:
        return len(self.rules_applied)

    def __repr__(self) -> str:
        return (
            f"MigrationResult(source={self.source_file!r}, "
            f"migrated={self.total_migrated}, "
            f"unmatched={len(self.unmatched_keys)})"
        )


def _apply_transform(value: str, transform: Optional[str]) -> str:
    if transform == "upper":
        return value.upper()
    if transform == "lower":
        return value.lower()
    return value


def migrate_entries(
    entries: List[EnvEntry],
    rules: List[MigrationRule],
    source_file: str = "<unknown>",
    skip_missing: bool = True,
) -> MigrationResult:
    """Apply migration rules to a list of EnvEntry objects."""
    rule_map: Dict[str, MigrationRule] = {r.old_key: r for r in rules}
    result = MigrationResult(source_file=source_file)
    matched_old_keys: set = set()

    for entry in entries:
        if entry.key is None:
            result.migrated.append(entry)
            continue

        if entry.key in rule_map:
            rule = rule_map[entry.key]
            new_value = _apply_transform(entry.value or "", rule.transform)
            new_entry = EnvEntry(
                key=rule.new_key,
                value=new_value,
                comment=entry.comment,
                raw=entry.raw,
            )
            result.migrated.append(new_entry)
            result.rules_applied.append(rule)
            matched_old_keys.add(entry.key)
        else:
            result.migrated.append(entry)
            result.unmatched_keys.append(entry.key)

    for rule in rules:
        if rule.old_key not in matched_old_keys:
            if skip_missing:
                result.skipped_keys.append(rule.old_key)

    return result

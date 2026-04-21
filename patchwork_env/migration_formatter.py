"""Format migration results for CLI output."""
from __future__ import annotations

from typing import List

from patchwork_env.env_migrator import MigrationResult, MigrationRule


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_migration_result(result: MigrationResult) -> str:
    lines: List[str] = []
    lines.append(_c(f"Migration Report: {result.source_file}", "1;36"))
    lines.append("-" * 52)

    if not result.rules_applied and not result.unmatched_keys:
        lines.append(_c("  No rules matched any keys.", "33"))
        return "\n".join(lines)

    if result.rules_applied:
        lines.append(_c("  Renamed keys:", "1"))
        for rule in result.rules_applied:
            old = _c(rule.old_key, "31")
            new = _c(rule.new_key, "32")
            suffix = f"  [{rule.transform}]" if rule.transform else ""
            lines.append(f"    {old}  ->  {new}{suffix}")

    if result.skipped_keys:
        lines.append(_c("  Skipped (key not found in source):", "33"))
        for key in result.skipped_keys:
            lines.append(f"    {_c(key, '33')}")

    if result.unmatched_keys:
        lines.append(_c("  Unmatched keys (passed through):", "90"))
        for key in result.unmatched_keys[:5]:
            lines.append(f"    {_c(key, '90')}")
        if len(result.unmatched_keys) > 5:
            lines.append(f"    ... and {len(result.unmatched_keys) - 5} more")

    return "\n".join(lines)


def format_migration_summary(result: MigrationResult) -> str:
    parts = [
        _c(f"Migrated {result.total_migrated} key(s)", "32"),
        _c(f"{len(result.skipped_keys)} skipped", "33"),
        _c(f"{len(result.unmatched_keys)} unchanged", "90"),
    ]
    return "  ".join(parts)

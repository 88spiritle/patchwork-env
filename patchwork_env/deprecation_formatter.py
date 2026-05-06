"""Formatting helpers for deprecation reports."""
from __future__ import annotations

from patchwork_env.env_deprecator import DeprecationReport, DeprecationRegistry


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_deprecation_report(report: DeprecationReport) -> str:
    lines = []
    lines.append(_c(f"Deprecation Report: {report.filename}", "1;34"))
    lines.append("-" * 48)

    if not report.has_deprecated:
        lines.append(_c("  ✔ No deprecated keys found.", "32"))
        return "\n".join(lines)

    for hit in report.hits:
        rec = hit.record
        tag = _c("DEPRECATED", "1;33")
        lines.append(f"  {tag}  {_c(hit.key, '33')}")
        if rec.reason:
            lines.append(f"           reason      : {rec.reason}")
        if rec.replacement:
            lines.append(f"           replacement : {_c(rec.replacement, '36')}")

    return "\n".join(lines)


def format_deprecation_summary(report: DeprecationReport) -> str:
    count = len(report.hits)
    if count == 0:
        return _c(f"{report.filename}: no deprecated keys", "32")
    noun = "key" if count == 1 else "keys"
    return _c(f"{report.filename}: {count} deprecated {noun} detected", "1;33")


def format_registry(registry: DeprecationRegistry) -> str:
    records = registry.all_records()
    lines = [_c("Registered Deprecated Keys", "1;34"), "-" * 40]
    if not records:
        lines.append("  (none)")
        return "\n".join(lines)
    for rec in records:
        suffix = f"  →  {rec.replacement}" if rec.replacement else ""
        lines.append(f"  {_c(rec.key, '33')}{suffix}")
        if rec.reason:
            lines.append(f"      {rec.reason}")
    return "\n".join(lines)

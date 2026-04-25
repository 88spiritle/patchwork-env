"""Formatting helpers for baseline and drift reports."""
from __future__ import annotations

from typing import List

from patchwork_env.env_baseline import Baseline, BaselineDrift


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_baseline(baseline: Baseline) -> str:
    lines = [
        _c("1;34", f"Baseline: {baseline.name}"),
        _c("2", f"  Created : {baseline.created_at}"),
        _c("2", f"  Entries : {len(baseline.entries)}"),
        "",
    ]
    for entry in sorted(baseline.entries, key=lambda e: e.key):
        lines.append(f"  {_c('36', entry.key):<30}  {entry.value}")
    return "\n".join(lines)


def format_drift_report(drifts: List[BaselineDrift], baseline_name: str, snapshot_filename: str) -> str:
    lines = [
        _c("1;33", f"Drift Report — baseline: {baseline_name}  vs  {snapshot_filename}"),
        "",
    ]
    if not drifts:
        lines.append(_c("32", "  ✔ No drift detected."))
        return "\n".join(lines)

    for d in drifts:
        if d.status == "added":
            lines.append(_c("32", f"  + {d.key}") + f"  (new value: {d.current_value!r})")
        elif d.status == "removed":
            lines.append(_c("31", f"  - {d.key}") + f"  (was: {d.baseline_value!r})")
        else:
            lines.append(
                _c("33", f"  ~ {d.key}")
                + f"  {d.baseline_value!r} → {d.current_value!r}"
            )
    return "\n".join(lines)


def format_drift_summary(drifts: List[BaselineDrift]) -> str:
    added = sum(1 for d in drifts if d.status == "added")
    removed = sum(1 for d in drifts if d.status == "removed")
    changed = sum(1 for d in drifts if d.status == "changed")
    parts = []
    if added:
        parts.append(_c("32", f"+{added} added"))
    if removed:
        parts.append(_c("31", f"-{removed} removed"))
    if changed:
        parts.append(_c("33", f"~{changed} changed"))
    if not parts:
        return _c("32", "No drift.")
    return "  ".join(parts)
